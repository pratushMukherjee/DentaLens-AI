"""Unit tests for evaluation metrics."""

import pytest

from dentalens.services.evaluation.metrics.responsible_ai import ResponsibleAIChecker


class TestResponsibleAIChecker:
    @pytest.fixture
    def checker(self):
        return ResponsibleAIChecker()

    def test_no_flags_clean_response(self, checker):
        response = "The PPO Gold plan covers root canals at 80% after deductible."
        flags = checker.check(response)
        assert len(flags) == 0

    def test_detects_ssn(self, checker):
        response = "Your SSN 123-45-6789 has been noted."
        flags = checker.check(response)
        assert any("PII_LEAKAGE" in f for f in flags)

    def test_detects_phone(self, checker):
        response = "Call us at (517) 555-1234 for more information."
        flags = checker.check(response)
        assert any("PII_LEAKAGE" in f for f in flags)

    def test_detects_email(self, checker):
        response = "Send documents to patient@email.com."
        flags = checker.check(response)
        assert any("PII_LEAKAGE" in f for f in flags)

    def test_detects_medical_advice(self, checker):
        response = "I recommend getting a root canal as soon as possible."
        flags = checker.check(response)
        assert any("MEDICAL_ADVICE" in f for f in flags)

    def test_detects_bias(self, checker):
        response = "People like you typically need more dental work."
        flags = checker.check(response)
        assert any("BIAS" in f for f in flags)

    def test_no_false_positive_on_dental_terms(self, checker):
        response = "Crown coverage is available at 50% under Major Services."
        flags = checker.check(response)
        assert len(flags) == 0
