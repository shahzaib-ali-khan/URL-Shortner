import re
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, HttpUrl, field_validator


class URLCreate(BaseModel):
    """Schema for creating a shortened URL."""

    original_url: HttpUrl
    preferred_short_code: Optional[str] = Field(
        default=None,
        min_length=3,
        max_length=50,
        description="Preferred custom short code (alphanumeric, hyphens, underscores only)",
    )
    title: Optional[str] = Field(default=None, max_length=255)

    @field_validator("preferred_short_code")
    @classmethod
    def validate_short_code(cls, v: Optional[str]) -> Optional[str]:
        """Validate that short code contains only allowed characters."""
        if v is not None:
            # Only allow alphanumeric, hyphens, and underscores
            if not re.match(r"^[a-zA-Z0-9_-]+$", v):
                raise ValueError(
                    "Short code can only contain letters, numbers, hyphens, and underscores"
                )
            # Reserved words that shouldn't be used as short codes
            reserved = {
                "api",
                "admin",
                "login",
                "signup",
                "logout",
                "docs",
                "redoc",
                "auth",
            }
            if v.lower() in reserved:
                raise ValueError(f'Short code "{v}" is reserved and cannot be used')
        return v


class URLUpdate(BaseModel):
    """Schema for updating a URL."""

    title: Optional[str] = Field(default=None, max_length=255)
    is_active: Optional[bool] = None


class URLResponse(BaseModel):
    """Schema for URL response."""

    id: str
    original_url: str
    short_code: str
    short_url: str  # Full shortened URL
    title: Optional[str]
    clicks: int
    is_active: bool
    created_at: datetime
    user_id: str

    class Config:
        from_attributes = True


class URLListResponse(BaseModel):
    """Schema for paginated URL list response."""

    urls: list[URLResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class URLStatsResponse(BaseModel):
    """Schema for URL statistics."""

    short_code: str
    original_url: str
    clicks: int
    created_at: datetime
    is_active: bool


class URLResolveResponse(BaseModel):
    """Schema for URL resolve."""

    short_code: str
    original_url: str
