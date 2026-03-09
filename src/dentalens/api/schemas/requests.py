"""Pydantic request schemas for the REST API."""

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Request body for chat endpoints."""

    conversation_id: str | None = None
    message: str = Field(..., min_length=1, max_length=2000)


class BenefitsQueryRequest(BaseModel):
    """Request body for direct benefits queries (bypasses router)."""

    query: str = Field(..., min_length=1, max_length=2000)
    plan_id: str | None = None


class EvaluationRequest(BaseModel):
    """Request body for evaluating a single response."""

    query: str
    response: str
    contexts: list[str]


class BatchEvaluationRequest(BaseModel):
    """Request body for batch evaluation."""

    samples: list[EvaluationRequest]
