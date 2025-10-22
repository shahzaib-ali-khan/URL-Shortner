from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel

from app.services.util import generate_uuid


class URL(SQLModel, table=True):
    """URL database model for storing shortened URLs."""

    __tablename__ = "urls"

    id: str = Field(default_factory=generate_uuid, primary_key=True)
    original_url: str = Field(nullable=False, index=True)
    short_code: str = Field(unique=True, index=True, nullable=False)
    user_id: str = Field(foreign_key="users.id", nullable=False, index=True)
    title: Optional[str] = Field(default=None, max_length=255)
    clicks: int = Field(default=0)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # user: Optional["User"] = Relationship(back_populates="urls")
