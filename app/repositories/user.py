from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.models.user import User


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, user: User) -> User:
        """Create a new user in the database."""
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def get_by_id(self, user_id: int) -> Optional[User]:
        """Retrieve user by ID."""
        statement = select(User).where(User.id == user_id)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[User]:
        """Retrieve user by email."""
        statement = select(User).where(User.email == email)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def update(self, user: User) -> User:
        """Update user in the database."""
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user
