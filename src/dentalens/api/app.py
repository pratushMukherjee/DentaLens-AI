"""FastAPI application factory with lifespan events."""

from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from dentalens import __version__
from dentalens.api.middleware.error_handler import (
    dentalens_exception_handler,
    generic_exception_handler,
)
from dentalens.api.middleware.request_logging import RequestLoggingMiddleware
from dentalens.api.routers import benefits, chat, claims, evaluation, health
from dentalens.config.logging_config import setup_logging
from dentalens.config.settings import Settings
from dentalens.domain.exceptions import DentaLensError


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan — initialize resources on startup, cleanup on shutdown."""
    settings = Settings()
    setup_logging(settings.log_level)
    yield


def create_app() -> FastAPI:
    """Application factory pattern — creates and configures the FastAPI app."""
    app = FastAPI(
        title="DentaLens AI",
        description="Enterprise AI platform for dental insurance — RAG, multi-agent systems, and responsible AI",
        version=__version__,
        lifespan=lifespan,
    )

    # Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(RequestLoggingMiddleware)

    # Exception handlers
    app.add_exception_handler(DentaLensError, dentalens_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)

    # Routers
    app.include_router(health.router)
    app.include_router(chat.router)
    app.include_router(claims.router)
    app.include_router(benefits.router)
    app.include_router(evaluation.router)

    return app
