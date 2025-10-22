"""Main FastAPI application."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.config import settings
from app.database import db_manager


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    await db_manager.create_db_and_tables()
    yield
    await db_manager.close()


def create_application() -> FastAPI:
    application = FastAPI(
        title=settings.APP_NAME,
        description="FastAPI application with JWT authentication",
        version="1.0.0",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # Configure CORS
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include API routers
    application.include_router(api_router, prefix="/api")

    return application


app = create_application()


@app.get("/", tags=["Health"])
async def root() -> dict[str, str]:
    """Root endpoint for health check."""
    return {"message": "FastAPI Auth App is running", "status": "healthy"}
