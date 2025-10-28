from typing import Optional

from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.api.v1.filters.url_filter import URLFilter
from app.models.url import URL


class URLRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, url: URL) -> URL:
        """Create a new URL in the database."""
        self.session.add(url)
        await self.session.commit()
        await self.session.refresh(url)
        return url

    async def get_by_id(self, url_id: str) -> Optional[URL]:
        """Retrieve URL by ID."""
        statement = select(URL).where(URL.id == url_id)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def get_by_short_code(self, short_code: str) -> Optional[URL]:
        """Retrieve URL by short code."""
        statement = select(URL).where(URL.short_code == short_code)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def get_by_user_id(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[URLFilter] = None,
    ) -> list[URL]:
        """Get all URLs for a user with pagination."""
        statement = (
            select(URL)
            .where(URL.user_id == user_id)
            .order_by(URL.created_at.desc())
            .offset(skip)
            .limit(limit)
        )

        if filters:
            statement = filters.filter(statement)

        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def count_by_user_id(
        self, user_id: str, filters: Optional[URLFilter] = None
    ) -> int:
        """Count total URLs for a user."""
        statement = select(func.count(URL.id)).where(URL.user_id == user_id)

        if filters:
            statement = filters.filter(statement)

        result = await self.session.execute(statement)
        return result.scalar_one()

    async def update(self, url: URL) -> URL:
        """Update URL in the database."""
        self.session.add(url)
        await self.session.commit()
        await self.session.refresh(url)
        return url

    async def delete(self, url: URL) -> None:
        """Delete URL from the database."""
        await self.session.delete(url)
        await self.session.commit()

    async def increment_clicks(self, url: URL) -> URL:
        """Increment click count for a URL."""
        url.clicks += 1
        return await self.update(url)
