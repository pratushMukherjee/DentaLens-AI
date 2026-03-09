"""Pydantic response schemas for the REST API."""

from typing import Any

from pydantic import BaseModel, Field


class SourceReference(BaseModel):
    """A reference to a source document used in a response."""

    document: str
    document_type: str | None = None
    relevance_score: float | None = None


class ChatResponse(BaseModel):
    """Response from the chat endpoint."""

    conversation_id: str
    response: str
    agent_used: str
    sources: list[SourceReference] = Field(default_factory=list)
    confidence: float | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class ClaimSummaryResponse(BaseModel):
    """Aggregated claims statistics."""

    total_claims: int
    total_billed: float
    total_paid: float
    avg_billed: float
    avg_paid: float
    approval_rate: float
    status_counts: dict[str, int]
    category_counts: dict[str, int]


class AnomalyResponse(BaseModel):
    """A detected billing anomaly."""

    claim_id: str
    procedure_code: str
    billed_amount: float
    typical_mean: float
    typical_std: float
    deviation: float
    reason: str


class PlanSummaryResponse(BaseModel):
    """Brief summary of a benefit plan."""

    plan_id: str
    plan_name: str
    plan_type: str
    annual_maximum: float
    deductible_individual: float


class EvaluationResponse(BaseModel):
    """Result of evaluating a single response."""

    query: str
    faithfulness_score: float
    relevance_score: float
    hallucination_detected: bool
    responsible_ai_flags: list[str]
    latency_ms: float


class EvalReportResponse(BaseModel):
    """Aggregated evaluation report."""

    total_queries: int
    avg_faithfulness: float
    avg_relevance: float
    hallucination_rate: float
    responsible_ai_flag_counts: dict[str, int]
    avg_latency_ms: float
    results: list[EvaluationResponse]


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    version: str
    components: dict[str, str] = Field(default_factory=dict)
