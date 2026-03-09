"""Claims data endpoints — statistics, anomaly detection, claim lookup."""

from fastapi import APIRouter, Depends, Query

from dentalens.api.dependencies import get_claims_repository
from dentalens.api.schemas.responses import AnomalyResponse, ClaimSummaryResponse
from dentalens.domain.enums import ClaimStatus
from dentalens.infrastructure.data.claims_repository import ClaimsRepository

router = APIRouter(prefix="/api/v1/claims", tags=["claims"])


@router.get("", summary="List claims with optional filtering")
async def list_claims(
    status: ClaimStatus | None = None,
    limit: int = Query(default=50, le=500),
    offset: int = Query(default=0, ge=0),
    repo: ClaimsRepository = Depends(get_claims_repository),
) -> dict:
    """List claims with optional status filtering."""
    if status:
        claims = repo.get_claims_by_status(status)
    else:
        claims = repo.get_all_claims()

    paginated = claims[offset:offset + limit]
    return {
        "total": len(claims),
        "offset": offset,
        "limit": limit,
        "claims": [c.model_dump(mode="json") for c in paginated],
    }


@router.get("/{claim_id}", summary="Get a single claim by ID")
async def get_claim(
    claim_id: str,
    repo: ClaimsRepository = Depends(get_claims_repository),
) -> dict:
    """Get a single claim by its ID."""
    claim = repo.get_claim_by_id(claim_id)
    if claim is None:
        return {"error": f"Claim {claim_id} not found"}
    return claim.model_dump(mode="json")


@router.get("/analysis/summary", response_model=ClaimSummaryResponse)
async def claims_summary(
    repo: ClaimsRepository = Depends(get_claims_repository),
) -> ClaimSummaryResponse:
    """Get aggregate claims statistics."""
    summary = repo.get_claims_summary()
    return ClaimSummaryResponse(**summary)


@router.get("/analysis/anomalies", response_model=list[AnomalyResponse])
async def claims_anomalies(
    repo: ClaimsRepository = Depends(get_claims_repository),
) -> list[AnomalyResponse]:
    """Detect billing anomalies in claims data."""
    anomalies = repo.detect_anomalies()
    return [AnomalyResponse(**a) for a in anomalies]
