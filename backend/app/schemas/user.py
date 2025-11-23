"""User schemas."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    """Base user schema."""

    username: str
    email: EmailStr


class UserCreate(UserBase):
    """User creation schema."""

    password: str


class UserUpdate(BaseModel):
    """User update schema."""

    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    status: Optional[str] = None


class UserResponse(UserBase):
    """User response schema."""

    id: int
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    status: str
    created_at: datetime
    roles: list[str] = []

    class Config:
        from_attributes = True


class Token(BaseModel):
    """Token response schema."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenPayload(BaseModel):
    """Token payload schema."""

    sub: str
    exp: datetime
    type: str


class LoginRequest(BaseModel):
    """Login request schema."""

    username: str
    password: str


class RefreshTokenRequest(BaseModel):
    """Refresh token request schema."""

    refresh_token: str
