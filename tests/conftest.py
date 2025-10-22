# ...existing code...
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import (AsyncSession, async_sessionmaker,
                                    create_async_engine)
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel

from app.database import db_manager, get_session
from app.main import app

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


@pytest_asyncio.fixture(scope="session")
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
