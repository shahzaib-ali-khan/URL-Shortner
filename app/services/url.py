from datetime import datetime, timezone
from typing import Optional

from fastapi import HTTPException, status

from app.models.url import URL
from app.repositories.url import URLRepository
from app.schemas.url import URLCreate, URLUpdate
from app.services.short_code_generator import (IShortCodeGenerator,
                                               default_generator)
import structlog

logger = structlog.get_logger(__name__)

class URLService:
    MAX_RETRIES = 5  # Maximum retries for generating unique short code

    def __init__(
        self,
        url_repository: URLRepository,
        short_code_generator: IShortCodeGenerator = default_generator,
    ) -> None:
        self.url_repository = url_repository
        self.short_code_generator = short_code_generator

    async def create_short_url(self, url_data: URLCreate, user_id: str) -> URL:
        """
        Create a shortened URL.

        If preferred_short_code is provided and available, use it.
        Otherwise, generate a random short code.
        """
        short_code: Optional[str] = None

        # Try to use preferred short code if provided
        if url_data.preferred_short_code:
            existing = await self.url_repository.get_by_short_code(
                url_data.preferred_short_code
            )

            if existing:
                logger.info("Preferred short code taken, generating random code",
                            preferred_short_code=url_data.preferred_short_code)
                # Preferred code is taken, fall back to random generation
                short_code = await self._generate_unique_short_code()
            else:
                # Preferred code is available
                short_code = url_data.preferred_short_code
        else:
            # No preference, generate random code
            short_code = await self._generate_unique_short_code()

        # Create URL record
        url = URL(
            original_url=str(url_data.original_url),
            short_code=short_code,
            user_id=user_id,
            title=url_data.title,
        )

        return await self.url_repository.create(url)

    async def _generate_unique_short_code(self, length: int = 6) -> str:
        """
        Generate a unique short code that doesn't exist in the database.

        Args:
            length: Length of the short code

        Returns:
            A unique short code

        Raises:
            HTTPException: If unable to generate unique code after max retries
        """
        for attempt in range(self.MAX_RETRIES):
            short_code = self.short_code_generator.generate(length)

            # Check if short code already exists
            existing = await self.url_repository.get_by_short_code(short_code)

            if not existing:
                return short_code

            # If collision on last attempt with base length, increase length
            if attempt == self.MAX_RETRIES - 1:
                length += 1

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to generate unique short code. Please try again.",
        )

    async def get_url_by_short_code(self, short_code: str) -> URL:
        """Get URL by short code."""
        url = await self.url_repository.get_by_short_code(short_code)

        if not url:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Short URL not found"
            )

        if not url.is_active:
            raise HTTPException(
                status_code=status.HTTP_410_GONE,
                detail="This short URL has been deactivated",
            )

        return url

    async def get_user_urls(
        self, user_id: str, page: int = 1, page_size: int = 20
    ) -> tuple[list[URL], int]:
        """
        Get all URLs for a user with pagination.

        Returns:
            Tuple of (list of URLs, total count)
        """
        skip = (page - 1) * page_size
        urls = await self.url_repository.get_by_user_id(user_id, skip, page_size)
        total = await self.url_repository.count_by_user_id(user_id)
        return urls, total

    async def update_url(
        self, short_code: str, url_update: URLUpdate, user_id: str
    ) -> URL:
        """Update a URL (only by owner)."""
        url = await self.url_repository.get_by_short_code(short_code)

        if not url:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Short URL not found"
            )

        # Check ownership
        if url.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to update this URL",
            )

        # Update fields
        if url_update.title is not None:
            url.title = url_update.title
        if url_update.is_active is not None:
            url.is_active = url_update.is_active

        url.updated_at = datetime.now(timezone.utc)

        return await self.url_repository.update(url)

    async def delete_url(self, short_code: str, user_id: str) -> None:
        """Delete a URL (only by owner)."""
        url = await self.url_repository.get_by_short_code(short_code)

        if not url:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Short URL not found"
            )

        # Check ownership
        if url.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to delete this URL",
            )

        await self.url_repository.delete(url)

    async def increment_click(self, short_code: str) -> URL:
        """Increment click count for a URL."""
        url = await self.get_url_by_short_code(short_code)
        return await self.url_repository.increment_clicks(url)
