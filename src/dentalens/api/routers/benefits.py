"""Benefits endpoints — plan info and RAG-powered Q&A."""

from fastapi import APIRouter, Depends, HTTPException

from dentalens.api.dependencies import get_retrieval_service
from dentalens.api.schemas.requests import BenefitsQueryRequest
from dentalens.api.schemas.responses import PlanSummaryResponse, SourceReference
from dentalens.config.constants import COLLECTION_BENEFIT_PLANS
from dentalens.services.rag.retrieval_service import RetrievalService

router = APIRouter(prefix="/api/v1/benefits", tags=["benefits"])

# Static plan data (in production, this would come from a database)
_PLANS = [
    PlanSummaryResponse(
        plan_id="DD-PPO-GOLD-2024", plan_name="Delta Dental PPO Gold",
        plan_type="PPO", annual_maximum=2000, deductible_individual=50,
    ),
    PlanSummaryResponse(
        plan_id="DD-PPO-SILVER-2024", plan_name="Delta Dental PPO Silver",
        plan_type="PPO", annual_maximum=1500, deductible_individual=75,
    ),
    PlanSummaryResponse(
        plan_id="DD-HMO-BASIC-2024", plan_name="Delta Dental HMO Basic",
        plan_type="HMO", annual_maximum=0, deductible_individual=0,
    ),
]


@router.get("/plans", response_model=list[PlanSummaryResponse])
async def list_plans() -> list[PlanSummaryResponse]:
    """List available benefit plan summaries."""
    return _PLANS


@router.get("/plans/{plan_id}", response_model=PlanSummaryResponse)
async def get_plan(plan_id: str) -> PlanSummaryResponse:
    """Get a specific plan's summary."""
    for plan in _PLANS:
        if plan.plan_id == plan_id:
            return plan
    raise HTTPException(status_code=404, detail=f"Plan {plan_id} not found")


@router.post("/query", summary="Ask a benefits question using RAG")
async def query_benefits(
    request: BenefitsQueryRequest,
    retrieval: RetrievalService = Depends(get_retrieval_service),
) -> dict:
    """Answer a benefits question using RAG retrieval (bypasses router agent)."""
    rag_response = await retrieval.retrieve_and_generate(
        query=request.query,
        collection_names=[COLLECTION_BENEFIT_PLANS],
    )

    sources = [
        SourceReference(
            document=s.source_file,
            document_type=s.document_type,
            relevance_score=s.relevance_score,
        )
        for s in rag_response.sources
    ]

    return {
        "query": request.query,
        "answer": rag_response.answer,
        "sources": [s.model_dump() for s in sources],
    }
