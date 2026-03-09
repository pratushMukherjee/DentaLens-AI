"""Evaluation endpoints — run quality assessments on RAG responses."""

from fastapi import APIRouter, Depends

from dentalens.api.dependencies import get_evaluation_pipeline
from dentalens.api.schemas.requests import BatchEvaluationRequest, EvaluationRequest
from dentalens.api.schemas.responses import EvalReportResponse, EvaluationResponse
from dentalens.services.evaluation.evaluator import EvaluationPipeline

router = APIRouter(prefix="/api/v1/evaluate", tags=["evaluation"])


@router.post("", response_model=EvaluationResponse)
async def evaluate_single(
    request: EvaluationRequest,
    pipeline: EvaluationPipeline = Depends(get_evaluation_pipeline),
) -> EvaluationResponse:
    """Evaluate a single query-response pair."""
    result = await pipeline.evaluate(
        query=request.query,
        response=request.response,
        contexts=request.contexts,
    )
    return EvaluationResponse(
        query=result.query,
        faithfulness_score=result.faithfulness_score,
        relevance_score=result.relevance_score,
        hallucination_detected=result.hallucination_detected,
        responsible_ai_flags=result.responsible_ai_flags,
        latency_ms=result.latency_ms,
    )


@router.post("/batch", response_model=EvalReportResponse)
async def evaluate_batch(
    request: BatchEvaluationRequest,
    pipeline: EvaluationPipeline = Depends(get_evaluation_pipeline),
) -> EvalReportResponse:
    """Evaluate a batch of query-response pairs and generate a report."""
    samples = [
        {"query": s.query, "response": s.response, "contexts": s.contexts}
        for s in request.samples
    ]
    results = await pipeline.evaluate_batch(samples)
    report = pipeline.generate_report(results)

    return EvalReportResponse(
        total_queries=report.total_queries,
        avg_faithfulness=report.avg_faithfulness,
        avg_relevance=report.avg_relevance,
        hallucination_rate=report.hallucination_rate,
        responsible_ai_flag_counts=report.responsible_ai_flag_counts,
        avg_latency_ms=report.avg_latency_ms,
        results=[
            EvaluationResponse(
                query=r.query,
                faithfulness_score=r.faithfulness_score,
                relevance_score=r.relevance_score,
                hallucination_detected=r.hallucination_detected,
                responsible_ai_flags=r.responsible_ai_flags,
                latency_ms=r.latency_ms,
            )
            for r in report.results
        ],
    )
