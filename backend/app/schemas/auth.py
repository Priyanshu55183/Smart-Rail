"""
Auth Schemas
============
Pydantic models for authentication request/response validation.

- UserRegister: Input for creating a new account
- UserLogin: Input for logging in
- UserResponse: What we return about the user (never includes password!)
- TokenResponse: JWT token response
"""

from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional


class UserRegister(BaseModel):
    """Registration request — name, email, and password."""
    name: str = Field(..., min_length=2, max_length=100, examples=["Priyanshu Sharma"])
    email: EmailStr = Field(..., examples=["priyanshu@example.com"])
    password: str = Field(..., min_length=6, max_length=128, examples=["securePass123"])


class UserLogin(BaseModel):
    """Login request — email and password."""
    email: EmailStr = Field(..., examples=["priyanshu@example.com"])
    password: str = Field(..., examples=["securePass123"])


class UserResponse(BaseModel):
    """User data returned to the frontend (NO password hash!)."""
    id: int
    name: str
    email: str
    created_at: datetime

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    """JWT token returned after login/register."""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
