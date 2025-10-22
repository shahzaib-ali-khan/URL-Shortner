from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.repositories.url import URLRepository
from app.services.url import URLService


async def get_url_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> URLRepository:
    """Get URL repository instance."""
    return URLRepository(session)


async def get_url_service(
    url_repository: Annotated[URLRepository, Depends(get_url_repository)],
) -> URLService:
    """Get URL service instance."""
    return URLService(url_repository)
