from typing import AsyncGenerator

import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import (AsyncSession, async_sessionmaker,
                                    create_async_engine)
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel

from app.database import get_session
from app.main import app
from app.models.url import URL
from app.models.user import User
from app.repositories.url import URLRepository
from app.repositories.user import UserRepository
from app.schemas.user import UserLogin
from app.security import password_hasher
from app.services.auth import AuthService

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_test_session() -> AsyncGenerator[AsyncSession, None]:
    async with TestSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


@pytest_asyncio.fixture
async def setup_database():
    """Create tables once per session and drop after."""
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)


@pytest_asyncio.fixture
async def override_dependencies(setup_database):
    """Override dependencies for testing."""
    app.dependency_overrides[get_session] = get_test_session
    yield
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def client(override_dependencies):
    """Async test client for FastAPI."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest_asyncio.fixture
async def user(setup_database) -> User:
    """Create a test user."""
    async with TestSessionLocal() as session:
        user_repo = UserRepository(session)
        user = User(
            email="foo@example.com",
            hashed_password=password_hasher.hash("testpassword123"),
        )
        created_user = await user_repo.create(user)
        await session.commit()
        return created_user


@pytest_asyncio.fixture
async def user_token(user: User) -> str:
    """Get a JWT token for the test user."""
    async with TestSessionLocal() as session:
        auth_service = AuthService(UserRepository(session))
        token = await auth_service.authenticate_user(
            UserLogin(email=user.email, password="testpassword123")
        )
        return token.access_token


@pytest_asyncio.fixture
async def url(user: User) -> URL:
    """Create a test URL for the test user."""
    async with TestSessionLocal() as session:
        url_repo = URLRepository(session)
        url = URL(
            original_url="http://example.com", short_code="abc123", user_id=user.id
        )
        created_url = await url_repo.create(url)
        await session.commit()
        return created_url
