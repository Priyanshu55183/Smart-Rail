"""
Security Service — Password Hashing & JWT Tokens
=================================================
Core authentication utilities used by the auth router.

- hash_password(): Create a bcrypt hash from plaintext
- verify_password(): Check plaintext against stored hash
- create_access_token(): Generate a signed JWT with expiry
- get_current_user(): FastAPI dependency that extracts and validates
  the JWT from the Authorization header, returning the User object.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database.postgres import get_db
from app.models.user import User

settings = get_settings()

# ── Password Hashing ─────────────────────────────────────
# CryptContext handles bcrypt hashing and verification.
# "deprecated='auto'" means if we ever switch algorithms,
# old hashes still verify but new ones use the latest scheme.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ── OAuth2 Bearer Token Scheme ────────────────────────────
# This tells FastAPI to look for "Authorization: Bearer <token>"
# in the request headers. The tokenUrl is used by Swagger UI.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)


def hash_password(password: str) -> str:
    """
    Hash a plaintext password using bcrypt.
    Returns a 60-character hash string like '$2b$12$...'
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plaintext password against a bcrypt hash.
    Returns True if they match, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a signed JWT token.

    Args:
        data: Payload to encode (usually {"sub": user_email})
        expires_delta: Custom expiration time (default: from settings)

    Returns:
        Encoded JWT string
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


async def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    FastAPI dependency — extracts the JWT from the Authorization header,
    decodes it, and returns the corresponding User from the database.

    Raises 401 if:
    - No token provided
    - Token is expired or malformed
    - User no longer exists in the database

    Usage in a route:
        @router.get("/protected")
        async def protected_route(user: User = Depends(get_current_user)):
            return {"message": f"Hello {user.name}"}
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if token is None:
        raise credentials_exception

    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        email: Optional[str] = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # Look up the user in the database
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception

    return user


async def get_current_user_optional(
    token: Optional[str] = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> Optional[User]:
    """
    Same as get_current_user but returns None instead of raising 401
    when no token is present. Useful for routes that work both with
    and without authentication.
    """
    if token is None:
        return None

    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        email: Optional[str] = payload.get("sub")
        if email is None:
            return None
    except JWTError:
        return None

    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()
