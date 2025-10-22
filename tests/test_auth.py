import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_signup_success(setup_database, override_dependencies):
    """Test successful user registration."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            "/api/v1/auth/signup",
            json={"email": "test@example.com", "password": "testpassword123"},
        )

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "id" in data
    assert "hashed_password" not in data


@pytest.mark.asyncio
async def test_signup_duplicate_email(setup_database, override_dependencies):
    """Test registration with duplicate email."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # First registration
        await client.post(
            "/api/v1/auth/signup",
            json={"email": "test@example.com", "password": "testpassword123"},
        )

        # Second registration with same email
        response = await client.post(
            "/api/v1/auth/signup",
            json={"email": "test@example.com", "password": "testpassword123"},
        )

    assert response.status_code == 400
    assert "already registered" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_login_success(setup_database, override_dependencies):
    """Test successful login."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Register user first
        await client.post(
            "/api/v1/auth/signup",
            json={"email": "test@example.com", "password": "testpassword123"},
        )

        # Login
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": "test@example.com", "password": "testpassword123"},
        )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_invalid_credentials(setup_database, override_dependencies):
    """Test login with invalid credentials."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": "test@example.com", "password": "wrongpassword"},
        )

    assert response.status_code == 401
    assert "incorrect" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_get_current_user(setup_database, override_dependencies):
    """Test getting current user information."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Register and login
        await client.post(
            "/api/v1/auth/signup",
            json={"email": "test@example.com", "password": "testpassword123"},
        )

        login_response = await client.post(
            "/api/v1/auth/login",
            json={"email": "test@example.com", "password": "testpassword123"},
        )
        token = login_response.json()["access_token"]

        # Get current user
        response = await client.get(
            "/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"}
        )

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"


@pytest.mark.asyncio
async def test_get_current_user_invalid_token(setup_database, override_dependencies):
    """Test getting current user with invalid token."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(
            "/api/v1/auth/me", headers={"Authorization": "Bearer invalid_token"}
        )

    assert response.status_code == 401
