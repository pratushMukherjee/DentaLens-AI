"""Unit tests for the RouterAgent intent classification."""

import json
from unittest.mock import AsyncMock, MagicMock

import pytest

from dentalens.domain.enums import IntentType
from dentalens.services.agents.router_agent import RouterAgent


@pytest.fixture
def router(mock_llm) -> RouterAgent:
    return RouterAgent(llm=mock_llm)


class TestKeywordClassification:
    def test_benefits_keywords(self, router):
        intent, confidence = router._keyword_classify("Is the root canal covered by the plan?")
        assert intent == IntentType.BENEFITS_QUESTION
        assert confidence >= 0.5

    def test_claims_keywords(self, router):
        intent, confidence = router._keyword_classify("Why was my claim denied?")
        assert intent == IntentType.CLAIMS_INQUIRY
        assert confidence >= 0.5

    def test_ambiguous_query(self, router):
        intent, confidence = router._keyword_classify("Hello, how are you?")
        assert intent == IntentType.UNKNOWN
        assert confidence == 0.0

    def test_multiple_benefits_keywords_higher_confidence(self, router):
        intent, conf = router._keyword_classify("What is the deductible and copay for the PPO plan coverage?")
        assert intent == IntentType.BENEFITS_QUESTION
        assert conf > 0.7

    def test_multiple_claims_keywords_higher_confidence(self, router):
        intent, conf = router._keyword_classify("Show denied claims with billing anomalies")
        assert intent == IntentType.CLAIMS_INQUIRY
        assert conf > 0.7


class TestLLMClassification:
    @pytest.mark.asyncio
    async def test_llm_classification_benefits(self, router, mock_llm):
        mock_llm.ainvoke = AsyncMock(return_value=MagicMock(
            content=json.dumps({
                "intent": "benefits_question",
                "confidence": 0.92,
                "reasoning": "User is asking about plan coverage"
            })
        ))
        intent, confidence, reasoning = await router._llm_classify("Tell me about my plan")
        assert intent == IntentType.BENEFITS_QUESTION
        assert confidence == 0.92

    @pytest.mark.asyncio
    async def test_llm_classification_parse_error(self, router, mock_llm):
        mock_llm.ainvoke = AsyncMock(return_value=MagicMock(content="not valid json"))
        intent, confidence, reasoning = await router._llm_classify("something")
        assert intent == IntentType.GENERAL
        assert confidence == 0.5


class TestFullClassification:
    @pytest.mark.asyncio
    async def test_high_confidence_keyword_skips_llm(self, router, mock_llm):
        intent, confidence = await router.classify("What does the PPO plan coverage include?")
        assert intent == IntentType.BENEFITS_QUESTION
        # LLM should NOT have been called (keyword confidence was high enough)
        mock_llm.ainvoke.assert_not_called()

    @pytest.mark.asyncio
    async def test_low_confidence_falls_through_to_llm(self, router, mock_llm):
        mock_llm.ainvoke = AsyncMock(return_value=MagicMock(
            content=json.dumps({
                "intent": "claims_inquiry",
                "confidence": 0.85,
                "reasoning": "User is asking about data"
            })
        ))
        intent, confidence = await router.classify("Show me the data")
        assert intent == IntentType.CLAIMS_INQUIRY
        mock_llm.ainvoke.assert_called_once()
