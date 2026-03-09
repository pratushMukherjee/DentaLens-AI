"""Unit tests for the Claim domain model."""

from datetime import date
from decimal import Decimal

import pytest
from pydantic import ValidationError

from dentalens.domain.enums import ClaimStatus
from dentalens.domain.models.claim import Claim


def test_valid_claim_creation():
    claim = Claim(
        claim_id="CLM-000001", patient_id="PAT-0001", provider_id="PROV-001",
        procedure_code="D1110", procedure_description="Adult cleaning",
        date_of_service=date(2024, 6, 15), billed_amount=Decimal("150.00"),
        allowed_amount=Decimal("130.00"), paid_amount=Decimal("130.00"),
        patient_responsibility=Decimal("0.00"), claim_status=ClaimStatus.APPROVED,
        plan_id="DD-PPO-GOLD-2024",
    )
    assert claim.claim_id == "CLM-000001"
    assert claim.claim_status == ClaimStatus.APPROVED
    assert claim.tooth_number is None


def test_claim_with_tooth_number():
    claim = Claim(
        claim_id="CLM-000002", patient_id="PAT-0002", provider_id="PROV-002",
        procedure_code="D2740", procedure_description="Crown",
        date_of_service=date(2024, 6, 15), billed_amount=Decimal("1200.00"),
        allowed_amount=Decimal("1000.00"), paid_amount=Decimal("500.00"),
        patient_responsibility=Decimal("500.00"), claim_status=ClaimStatus.APPROVED,
        plan_id="DD-PPO-GOLD-2024", tooth_number=14,
    )
    assert claim.tooth_number == 14


def test_claim_negative_amount_rejected():
    with pytest.raises(ValidationError):
        Claim(
            claim_id="CLM-BAD", patient_id="PAT-0001", provider_id="PROV-001",
            procedure_code="D1110", procedure_description="Cleaning",
            date_of_service=date(2024, 6, 15), billed_amount=Decimal("-50.00"),
            allowed_amount=Decimal("130.00"), paid_amount=Decimal("130.00"),
            patient_responsibility=Decimal("0.00"), claim_status=ClaimStatus.APPROVED,
            plan_id="DD-PPO-GOLD-2024",
        )


def test_claim_invalid_tooth_number():
    with pytest.raises(ValidationError):
        Claim(
            claim_id="CLM-BAD", patient_id="PAT-0001", provider_id="PROV-001",
            procedure_code="D2740", procedure_description="Crown",
            date_of_service=date(2024, 6, 15), billed_amount=Decimal("1200.00"),
            allowed_amount=Decimal("1000.00"), paid_amount=Decimal("500.00"),
            patient_responsibility=Decimal("500.00"), claim_status=ClaimStatus.APPROVED,
            plan_id="DD-PPO-GOLD-2024", tooth_number=33,
        )


def test_claim_all_statuses():
    for status in ClaimStatus:
        claim = Claim(
            claim_id=f"CLM-{status.value}", patient_id="PAT-0001", provider_id="PROV-001",
            procedure_code="D1110", procedure_description="Cleaning",
            date_of_service=date(2024, 6, 15), billed_amount=Decimal("100.00"),
            allowed_amount=Decimal("90.00"), paid_amount=Decimal("90.00"),
            patient_responsibility=Decimal("0.00"), claim_status=status,
            plan_id="DD-PPO-GOLD-2024",
        )
        assert claim.claim_status == status


def test_claim_serialization():
    claim = Claim(
        claim_id="CLM-SERIAL", patient_id="PAT-0001", provider_id="PROV-001",
        procedure_code="D1110", procedure_description="Cleaning",
        date_of_service=date(2024, 6, 15), billed_amount=Decimal("100.00"),
        allowed_amount=Decimal("90.00"), paid_amount=Decimal("90.00"),
        patient_responsibility=Decimal("0.00"), claim_status=ClaimStatus.APPROVED,
        plan_id="DD-PPO-GOLD-2024",
    )
    data = claim.model_dump(mode="json")
    assert data["claim_id"] == "CLM-SERIAL"
    assert data["date_of_service"] == "2024-06-15"
    assert data["claim_status"] == "approved"
