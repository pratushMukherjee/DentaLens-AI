"""Evaluation result domain models."""

from datetime import datetime, timezone

from pydantic import BaseModel, Field


class EvaluationResult(BaseModel):
    """Result of evaluating a single RAG response."""

    query: str
    response: str
    retrieved_contexts: list[str]
    faithfulness_score: float = Field(ge=0.0, le=1.0)
    relevance_score: float = Field(ge=0.0, le=1.0)
    hallucination_detected: bool
    responsible_ai_flags: list[str] = Field(default_factory=list)
    latency_ms: float
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class EvalReport(BaseModel):
    """Aggregated evaluation report across multiple queries."""

    total_queries: int
    avg_faithfulness: float
    avg_relevance: float
    hallucination_rate: float
    responsible_ai_flag_counts: dict[str, int] = Field(default_factory=dict)
    avg_latency_ms: float
    results: list[EvaluationResult]
