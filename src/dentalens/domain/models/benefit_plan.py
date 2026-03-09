"""Dental benefit plan domain model."""

from decimal import Decimal

from pydantic import BaseModel

from dentalens.domain.enums import PlanType


class BenefitPlan(BaseModel):
    """Represents a dental benefit plan with coverage details."""

    plan_id: str
    plan_name: str
    plan_type: PlanType
    annual_maximum: Decimal
    deductible_individual: Decimal
    deductible_family: Decimal
    preventive_coverage_pct: int
    basic_coverage_pct: int
    major_coverage_pct: int
    orthodontic_coverage_pct: int
    waiting_periods: dict[str, int] = {}
