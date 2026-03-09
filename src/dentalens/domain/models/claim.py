"""Dental claim domain model."""

from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field

from dentalens.domain.enums import ClaimStatus


class Claim(BaseModel):
    """Represents a dental insurance claim."""

    claim_id: str
    patient_id: str
    provider_id: str
    procedure_code: str = Field(description="CDT code, e.g. D0120")
    procedure_description: str
    date_of_service: date
    billed_amount: Decimal = Field(ge=0)
    allowed_amount: Decimal = Field(ge=0)
    paid_amount: Decimal = Field(ge=0)
    patient_responsibility: Decimal = Field(ge=0)
    claim_status: ClaimStatus
    plan_id: str
    tooth_number: int | None = Field(default=None, ge=1, le=32)
    surface: str | None = None
    diagnosis_code: str | None = None
