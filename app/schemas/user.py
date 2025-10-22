from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    """Schema for user creation."""

    password: str = Field(min_length=8, max_length=100)


class UserLogin(BaseModel):
    """Schema for user login."""

    email: EmailStr
    password: str


class UserResponse(UserBase):
    """Schema for user response."""

    id: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    """Schema for JWT token response."""

    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Schema for token payload data."""

    email: Optional[EmailStr] = None
