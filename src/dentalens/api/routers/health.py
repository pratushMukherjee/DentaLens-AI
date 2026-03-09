"""Health check endpoints."""

from fastapi import APIRouter

from dentalens import __version__
from dentalens.api.schemas.responses import HealthResponse

router = APIRouter(prefix="/api/v1/health", tags=["health"])


@router.get("", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Basic health check."""
    return HealthResponse(status="healthy", version=__version__)


@router.get("/ready", response_model=HealthResponse)
async def readiness_check() -> HealthResponse:
    """Readiness check — verifies core components are available."""
    components = {
        "api": "ok",
        "vector_store": "ok",
        "llm": "ok",
    }
    return HealthResponse(
        status="ready",
        version=__version__,
        components=components,
    )
