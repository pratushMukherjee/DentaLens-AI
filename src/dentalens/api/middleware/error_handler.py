"""Global exception handler middleware."""

import logging

from fastapi import Request
from fastapi.responses import JSONResponse

from dentalens.domain.exceptions import (
    AgentRoutingError,
    DentaLensError,
    DocumentNotFoundError,
    EmbeddingError,
    EvaluationError,
    LLMProviderError,
)

logger = logging.getLogger("dentalens.api.error")

_EXCEPTION_STATUS_MAP: dict[type, int] = {
    DocumentNotFoundError: 404,
    AgentRoutingError: 422,
    EmbeddingError: 503,
    LLMProviderError: 503,
    EvaluationError: 500,
}


async def dentalens_exception_handler(request: Request, exc: DentaLensError) -> JSONResponse:
    """Handle DentaLens domain exceptions with structured error responses."""
    status_code = _EXCEPTION_STATUS_MAP.get(type(exc), 500)
    error_type = type(exc).__name__

    logger.error("DentaLens error [%s]: %s (path=%s)", error_type, exc, request.url.path)

    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": error_type,
                "message": str(exc),
            }
        },
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions."""
    logger.exception("Unhandled exception (path=%s): %s", request.url.path, exc)

    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "InternalServerError",
                "message": "An unexpected error occurred",
            }
        },
    )
