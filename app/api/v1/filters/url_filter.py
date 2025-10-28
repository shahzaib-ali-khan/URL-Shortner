from typing import Optional

from fastapi_filter.contrib.sqlalchemy import Filter

from app.models.url import URL


class URLFilter(Filter):
    title__ilike: Optional[str] = None
    original_url__ilike: Optional[str] = None
    is_active: Optional[bool] = None
    created_at__gte: Optional[str] = None
    created_at__lte: Optional[str] = None

    class Constants(Filter.Constants):
        model = URL
        fields = ["title", "original_url", "is_active", "created_at"]
