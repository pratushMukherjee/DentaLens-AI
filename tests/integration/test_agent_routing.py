"""Integration tests for agent routing logic."""

import json
from unittest.mock import AsyncMock, MagicMock

import pytest

from dentalens.domain.enums import AgentType, IntentType
from dentalens.services.agents.agent_registry import AgentRegistry
from dentalens.services.agents.base_agent import AgentContext, AgentResponse, BaseAgent
from dentalens.services.agents.router_agent import RouterAgent


class MockSpecialistAgent(BaseAgent):
    """Mock specialist agent for testing routing."""

    def __init__(self, name: str, handled_intent: IntentType, **kwargs):
        super().__init__(name=name, description=f"Mock {name} agent", **kwargs)
        self._handled_intent = handled_intent

    async def process(self, query: str, context: AgentContext) -> AgentResponse:
        return AgentResponse(content=f"Response from {self.name}", agent_name=self.name)

    def can_handle(self, intent: IntentType) -> bool:
        return intent == self._handled_intent


@pytest.fixture
def registry(mock_llm):
    registry = AgentRegistry()

    benefits_agent = MockSpecialistAgent(
        name="benefits", handled_intent=IntentType.BENEFITS_QUESTION, llm=mock_llm
    )
    claims_agent = MockSpecialistAgent(
        name="claims", handled_intent=IntentType.CLAIMS_INQUIRY, llm=mock_llm
    )

    registry.register(AgentType.BENEFITS, benefits_agent)
    registry.register(AgentType.CLAIMS, claims_agent)
    return registry


def test_registry_get_by_type(registry):
    agent = registry.get(AgentType.BENEFITS)
    assert agent.name == "benefits"


def test_registry_get_for_intent(registry):
    agent = registry.get_for_intent(IntentType.BENEFITS_QUESTION)
    assert agent is not None
    assert agent.name == "benefits"


def test_registry_get_for_unknown_intent(registry):
    agent = registry.get_for_intent(IntentType.UNKNOWN)
    assert agent is None


@pytest.mark.asyncio
async def test_router_classifies_benefits_query(mock_llm):
    router = RouterAgent(llm=mock_llm)
    intent, confidence = await router.classify("Does the PPO plan cover crowns?")
    assert intent == IntentType.BENEFITS_QUESTION


@pytest.mark.asyncio
async def test_router_classifies_claims_query(mock_llm):
    router = RouterAgent(llm=mock_llm)
    intent, confidence = await router.classify("Show me denied claims")
    assert intent == IntentType.CLAIMS_INQUIRY


@pytest.mark.asyncio
async def test_full_routing_flow(mock_llm, registry):
    router = RouterAgent(llm=mock_llm)
    intent, confidence = await router.classify("What does my plan cover?")
    target_type = router.get_target_agent_type(intent)
    specialist = registry.get(target_type)
    response = await specialist.process("What does my plan cover?", AgentContext())
    assert response.agent_name == "benefits"
