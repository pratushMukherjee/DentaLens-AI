"""Unit tests for prompt template rendering."""

from dentalens.infrastructure.llm.prompt_templates import (
    BENEFITS_QA_SYSTEM_PROMPT,
    CLAIMS_ANALYSIS_SYSTEM_PROMPT,
    HALLUCINATION_CHECK_PROMPT,
    RELEVANCE_CHECK_PROMPT,
    ROUTER_SYSTEM_PROMPT,
)


def test_router_prompt_contains_intent_types():
    assert "benefits_question" in ROUTER_SYSTEM_PROMPT
    assert "claims_inquiry" in ROUTER_SYSTEM_PROMPT
    assert "general" in ROUTER_SYSTEM_PROMPT


def test_benefits_prompt_has_placeholders():
    rendered = BENEFITS_QA_SYSTEM_PROMPT.format(
        context="Test context about dental plans",
        history="user: What is covered?",
    )
    assert "Test context about dental plans" in rendered
    assert "What is covered?" in rendered


def test_claims_prompt_has_placeholders():
    rendered = CLAIMS_ANALYSIS_SYSTEM_PROMPT.format(
        context="Claims data here",
        history="No prior conversation.",
    )
    assert "Claims data here" in rendered


def test_hallucination_prompt_has_placeholders():
    rendered = HALLUCINATION_CHECK_PROMPT.format(
        context="The PPO Gold plan covers cleanings.",
        response="Cleanings are covered at 100%.",
    )
    assert "PPO Gold" in rendered
    assert "100%" in rendered


def test_relevance_prompt_has_placeholders():
    rendered = RELEVANCE_CHECK_PROMPT.format(
        query="Is my plan good?",
        response="Your plan offers comprehensive coverage.",
    )
    assert "Is my plan good?" in rendered
    assert "comprehensive coverage" in rendered


def test_router_prompt_requests_json():
    assert "JSON" in ROUTER_SYSTEM_PROMPT


def test_benefits_prompt_instructs_no_fabrication():
    assert "never fabricate" in BENEFITS_QA_SYSTEM_PROMPT.lower() or "only" in BENEFITS_QA_SYSTEM_PROMPT.lower()
