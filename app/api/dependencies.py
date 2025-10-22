from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.repositories.user import UserRepository
from app.schemas.user import UserResponse
from app.services.auth import AuthService

security = HTTPBearer()


async def get_user_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> UserRepository:
    """Get user repository instance."""
    return UserRepository(session)


async def get_auth_service(
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
) -> AuthService:
    """Get authentication service instance."""
    return AuthService(user_repository)


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> UserResponse:
    """Get current authenticated user."""
    token = credentials.credentials
    user = await auth_service.get_current_user(token)
    return UserResponse(
        id=user.id,
        email=user.email,
        is_active=user.is_active,
        created_at=user.created_at,
    )


async def get_current_active_user(
    current_user: Annotated[UserResponse, Depends(get_current_user)],
) -> UserResponse:
    """Get current active user."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )
    return current_user
