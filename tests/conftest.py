"""Shared test fixtures — mock LLM, vector store, sample data."""

from datetime import date
from decimal import Decimal
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

from dentalens.domain.enums import ClaimStatus
from dentalens.domain.models.claim import Claim
from dentalens.domain.models.conversation import Conversation, Message


@pytest.fixture
def sample_claims() -> list[Claim]:
    """A set of diverse sample claims for testing."""
    return [
        Claim(
            claim_id="CLM-000001", patient_id="PAT-0001", provider_id="PROV-001",
            procedure_code="D1110", procedure_description="Adult prophylaxis (cleaning)",
            date_of_service=date(2024, 3, 15), billed_amount=Decimal("150.00"),
            allowed_amount=Decimal("130.00"), paid_amount=Decimal("130.00"),
            patient_responsibility=Decimal("0.00"), claim_status=ClaimStatus.APPROVED,
            plan_id="DD-PPO-GOLD-2024",
        ),
        Claim(
            claim_id="CLM-000002", patient_id="PAT-0002", provider_id="PROV-002",
            procedure_code="D2740", procedure_description="Crown - porcelain/ceramic",
            date_of_service=date(2024, 5, 20), billed_amount=Decimal("1200.00"),
            allowed_amount=Decimal("1000.00"), paid_amount=Decimal("500.00"),
            patient_responsibility=Decimal("500.00"), claim_status=ClaimStatus.APPROVED,
            plan_id="DD-PPO-GOLD-2024", tooth_number=14,
        ),
        Claim(
            claim_id="CLM-000003", patient_id="PAT-0003", provider_id="PROV-003",
            procedure_code="D3330", procedure_description="Root canal - molar",
            date_of_service=date(2024, 7, 10), billed_amount=Decimal("3500.00"),
            allowed_amount=Decimal("1200.00"), paid_amount=Decimal("0.00"),
            patient_responsibility=Decimal("1200.00"), claim_status=ClaimStatus.DENIED,
            plan_id="DD-PPO-SILVER-2024", tooth_number=30,
        ),
        Claim(
            claim_id="CLM-000004", patient_id="PAT-0001", provider_id="PROV-001",
            procedure_code="D0120", procedure_description="Periodic oral evaluation",
            date_of_service=date(2024, 3, 15), billed_amount=Decimal("55.00"),
            allowed_amount=Decimal("50.00"), paid_amount=Decimal("50.00"),
            patient_responsibility=Decimal("0.00"), claim_status=ClaimStatus.APPROVED,
            plan_id="DD-PPO-GOLD-2024",
        ),
        Claim(
            claim_id="CLM-000005", patient_id="PAT-0004", provider_id="PROV-005",
            procedure_code="D7140", procedure_description="Extraction - erupted tooth",
            date_of_service=date(2024, 9, 1), billed_amount=Decimal("200.00"),
            allowed_amount=Decimal("175.00"), paid_amount=Decimal("140.00"),
            patient_responsibility=Decimal("35.00"), claim_status=ClaimStatus.PENDING,
            plan_id="DD-HMO-BASIC-2024", tooth_number=17,
        ),
    ]


@pytest.fixture
def sample_conversation() -> Conversation:
    """A pre-built conversation with sample messages."""
    conv = Conversation()
    conv.add_message("user", "Does the PPO Gold plan cover root canals?")
    conv.add_message(
        "assistant",
        "Yes, the PPO Gold plan covers root canal therapy under Basic Services at 80% after deductible.",
        agent_source="benefits",
    )
    conv.add_message("user", "What about the Silver plan?")
    conv.add_message(
        "assistant",
        "The Silver plan also covers root canals, but at 70% after deductible.",
        agent_source="benefits",
    )
    conv.add_message("user", "How many claims were denied?")
    return conv


@pytest.fixture
def mock_llm() -> MagicMock:
    """Mock LLM that returns canned responses."""
    llm = MagicMock()
    response = MagicMock()
    response.content = '{"intent": "benefits_question", "confidence": 0.9, "reasoning": "test"}'
    llm.ainvoke = AsyncMock(return_value=response)
    return llm


@pytest.fixture
def seed_data_dir() -> Path:
    """Path to the seed data directory."""
    return Path("data/seed")
