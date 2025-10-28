import pytest
from conftest import TestSessionLocal
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.models.url import URL
from app.models.user import User
from app.repositories.url import URLRepository


@pytest.mark.asyncio
async def test_shorten_url_success(
    setup_database, override_dependencies, user_token: str
):
    """Test successful URL shortening with valid token."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            "/api/v1/urls",
            json={
                "preferred_short_code": "nord",
                "original_url": "http://example.com",
                "title": "Example",
            },
            headers={"Authorization": f"Bearer {user_token}"},
        )
    assert response.status_code == 201
    data = response.json()
    assert data["original_url"] == "http://example.com/"
    assert "short_code" in data
    assert "short_url" in data
    assert data["short_url"] == "http://test/nord"


@pytest.mark.asyncio
async def test_shorten_url_unauthorized(setup_database, override_dependencies):
    """Test URL shortening without authentication."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            "/api/v1/urls",
            json={
                "preferred_short_code": "nord",
                "original_url": "http://example.com",
                "title": "Example",
            },
        )
    assert response.status_code == 403
    assert "not authenticated" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_shorten_url_uniquness(
    setup_database, override_dependencies, user_token: str, url: URL
):
    """Test successful URL shortening with valid token."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            "/api/v1/urls",
            json={
                "preferred_short_code": "abc123",
                "original_url": "http://example.com",
                "title": "Example",
            },
            headers={"Authorization": f"Bearer {user_token}"},
        )

    assert response.status_code == 201
    data = response.json()
    assert data["short_code"] != url.short_code


@pytest.mark.asyncio
async def test_resolve_url(setup_database, override_dependencies, url: URL):
    """Test successful URL shortening with valid token."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(
            f"/api/v1/urls/{url.short_code}/resolve",
        )

    assert response.status_code == 200
    data = response.json()
    assert "original_url" in data


@pytest.mark.asyncio
async def test_shorten_url_patch(
    setup_database, override_dependencies, user_token: str, url: URL
):
    """Test successful URL shortening with valid token."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.patch(
            f"/api/v1/urls/{url.short_code}",
            json={
                "is_active": False,
            },
            headers={"Authorization": f"Bearer {user_token}"},
        )
    assert response.status_code == 200
    data = response.json()
    assert not data["is_active"]


@pytest.mark.asyncio
async def test_shorten_url_delete(
    setup_database, override_dependencies, user_token: str, url: URL, user: User
):
    """Test successful URL shortening with valid token."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.delete(
            f"/api/v1/urls/{url.short_code}",
            headers={"Authorization": f"Bearer {user_token}"},
        )
    assert response.status_code == 204

    async with TestSessionLocal() as session:
        url_repo = URLRepository(session)
        url = URL(
            original_url="http://example.com", short_code="abc123", user_id=user.id
        )
        user_urls = await url_repo.get_by_user_id(user.id)
        assert len(user_urls) == 0
