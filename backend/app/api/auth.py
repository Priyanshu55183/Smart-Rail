"""
Auth API Router
===============
Handles user registration, login, and profile retrieval.

Endpoints:
  POST /api/auth/register  → Create account, return JWT
  POST /api/auth/login     → Verify credentials, return JWT
  GET  /api/auth/me        → Return current user profile (protected)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.postgres import get_db
from app.models.user import User
from app.schemas.auth import UserRegister, UserLogin, UserResponse, TokenResponse
from app.services.security import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user,
)

router = APIRouter()


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
async def register(data: UserRegister, db: AsyncSession = Depends(get_db)):
    """
    Create a new user account.

    - Checks if email is already taken
    - Hashes the password with bcrypt
    - Creates the User row in PostgreSQL
    - Returns a JWT access token + user profile
    """
    # Check if email already exists
    existing = await db.execute(select(User).where(User.email == data.email))
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists",
        )

    # Create user with hashed password
    user = User(
        name=data.name,
        email=data.email,
        password_hash=hash_password(data.password),
    )
    db.add(user)
    await db.flush()  # Get the auto-generated ID
    await db.refresh(user)  # Reload timestamps

    # Generate JWT
    token = create_access_token(data={"sub": user.email, "user_id": user.id})

    return TokenResponse(
        access_token=token,
        user=UserResponse.model_validate(user),
    )


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login with email and password",
)
async def login(data: UserLogin, db: AsyncSession = Depends(get_db)):
    """
    Authenticate a user and return a JWT.

    - Looks up the user by email
    - Verifies the password against the stored bcrypt hash
    - Returns a JWT access token + user profile
    """
    # Find user by email
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Generate JWT
    token = create_access_token(data={"sub": user.email, "user_id": user.id})

    return TokenResponse(
        access_token=token,
        user=UserResponse.model_validate(user),
    )


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user profile",
)
async def get_me(current_user: User = Depends(get_current_user)):
    """
    Return the profile of the currently authenticated user.
    Requires a valid JWT in the Authorization header.
    """
    return UserResponse.model_validate(current_user)
