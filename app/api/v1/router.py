from fastapi import APIRouter

from app.api.v1 import auth


api_router = APIRouter(prefix="/v1")

# Include all route modules
api_router.include_router(auth.router)
