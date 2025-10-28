from math import ceil
from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request, status
from fastapi_filter import FilterDepends

from app.api.dependencies.auth import get_current_active_user
from app.api.dependencies.url import get_url_service
from app.schemas.url import (URLCreate, URLListResponse, URLResolveResponse,
                             URLResponse, URLStatsResponse, URLUpdate)
from app.schemas.user import UserResponse
from app.services.url import URLService
from app.api.v1.filters.url_filter import URLFilter

router = APIRouter(prefix="/urls", tags=["URL Shortening"])


def build_short_url(request: Request, short_code: str) -> str:
    """Build the full short URL."""
    base_url = str(request.base_url).rstrip("/")
    return f"{base_url}/{short_code}"


@router.post(
    "",
    response_model=URLResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a shortened URL",
)
async def create_short_url(
    url_data: URLCreate,
    request: Request,
    current_user: Annotated[UserResponse, Depends(get_current_active_user)],
    url_service: Annotated[URLService, Depends(get_url_service)],
) -> URLResponse:
    """
    Create a shortened URL.

    - **original_url**: The URL to shorten (must be valid HTTP/HTTPS URL)
    - **preferred_short_code**: Optional custom short code (3-50 chars, alphanumeric + hyphens/underscores)
    - **title**: Optional title/description for the URL

    **Behavior:**
    - If `preferred_short_code` is provided AND available → uses it
    - If `preferred_short_code` is provided BUT taken → generates random code
    - If `preferred_short_code` is NOT provided → generates random code
    """
    url = await url_service.create_short_url(url_data, current_user.id)

    return URLResponse(
        id=url.id,
        original_url=url.original_url,
        short_code=url.short_code,
        short_url=build_short_url(request, url.short_code),
        title=url.title,
        clicks=url.clicks,
        is_active=url.is_active,
        created_at=url.created_at,
        user_id=url.user_id,
    )


@router.get("", response_model=URLListResponse, summary="Get all URLs for current user")
async def get_my_urls(
    request: Request,
    current_user: Annotated[UserResponse, Depends(get_current_active_user)],
    url_service: Annotated[URLService, Depends(get_url_service)],
    url_filter: URLFilter = FilterDepends(URLFilter),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
) -> URLListResponse:
    """
    Get all shortened URLs created by the current user with pagination.

    - **page**: Page number (starts from 1)
    - **page_size**: Number of items per page (1-100)
    """
    urls, total = await url_service.get_user_urls(current_user.id, page, page_size, url_filter)

    url_responses = [
        URLResponse(
            id=url.id,
            original_url=url.original_url,
            short_code=url.short_code,
            short_url=build_short_url(request, url.short_code),
            title=url.title,
            clicks=url.clicks,
            is_active=url.is_active,
            created_at=url.created_at,
            user_id=url.user_id,
        )
        for url in urls
    ]

    return URLListResponse(
        urls=url_responses,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=ceil(total / page_size) if total > 0 else 0,
    )


@router.get(
    "/{short_code}", response_model=URLResponse, summary="Get URL details by short code"
)
async def get_url(
    short_code: str,
    request: Request,
    current_user: Annotated[UserResponse, Depends(get_current_active_user)],
    url_service: Annotated[URLService, Depends(get_url_service)],
) -> URLResponse:
    """
    Get details of a specific shortened URL.

    - **short_code**: The short code of the URL
    """
    url = await url_service.get_url_by_short_code(short_code)

    return URLResponse(
        id=url.id,
        original_url=url.original_url,
        short_code=url.short_code,
        short_url=build_short_url(request, url.short_code),
        title=url.title,
        clicks=url.clicks,
        is_active=url.is_active,
        created_at=url.created_at,
        user_id=url.user_id,
    )


@router.get(
    "/{short_code}/stats", response_model=URLStatsResponse, summary="Get URL statistics"
)
async def get_url_stats(
    short_code: str,
    current_user: Annotated[UserResponse, Depends(get_current_active_user)],
    url_service: Annotated[URLService, Depends(get_url_service)],
) -> URLStatsResponse:
    """
    Get statistics for a shortened URL (clicks, creation date, etc.).

    - **short_code**: The short code of the URL
    """
    url = await url_service.get_url_by_short_code(short_code)

    return URLStatsResponse(
        short_code=url.short_code,
        original_url=url.original_url,
        clicks=url.clicks,
        created_at=url.created_at,
        is_active=url.is_active,
    )


@router.patch("/{short_code}", response_model=URLResponse, summary="Update URL details")
async def update_url(
    short_code: str,
    url_update: URLUpdate,
    request: Request,
    current_user: Annotated[UserResponse, Depends(get_current_active_user)],
    url_service: Annotated[URLService, Depends(get_url_service)],
) -> URLResponse:
    """
    Update a shortened URL (title, active status).

    Only the owner can update their URLs.

    - **short_code**: The short code of the URL to update
    - **title**: New title (optional)
    - **is_active**: Activate or deactivate the URL (optional)
    """
    url = await url_service.update_url(short_code, url_update, current_user.id)

    return URLResponse(
        id=url.id,
        original_url=url.original_url,
        short_code=url.short_code,
        short_url=build_short_url(request, url.short_code),
        title=url.title,
        clicks=url.clicks,
        is_active=url.is_active,
        created_at=url.created_at,
        user_id=url.user_id,
    )


@router.delete(
    "/{short_code}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a shortened URL",
)
async def delete_url(
    short_code: str,
    current_user: Annotated[UserResponse, Depends(get_current_active_user)],
    url_service: Annotated[URLService, Depends(get_url_service)],
) -> None:
    """
    Delete a shortened URL.

    Only the owner can delete their URLs.

    - **short_code**: The short code of the URL to delete
    """
    await url_service.delete_url(short_code, current_user.id)


@router.get(
    "/{short_code}/resolve",
    response_model=URLResolveResponse,
    summary="Get resolve URL",
    description="Returns original URL and short code associated with the short url. Frontend can use this to perform the redirect.",
)
async def get_resolve_url(
    short_code: str, url_service: Annotated[URLService, Depends(get_url_service)]
) -> URLResolveResponse:
    """
    Get original url for a shortened URL.

    - **short_code**: The short code of the URL
    """
    url = await url_service.get_url_by_short_code(short_code)

    return URLResolveResponse(
        short_code=url.short_code,
        original_url=url.original_url,
    )
