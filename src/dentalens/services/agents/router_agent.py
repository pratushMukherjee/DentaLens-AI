"""Router/triage agent — classifies intent and delegates to specialist agents."""

import json

from langchain_core.messages import HumanMessage, SystemMessage

from dentalens.config.constants import ROUTER_CONFIDENCE_THRESHOLD
from dentalens.domain.enums import AgentType, IntentType
from dentalens.domain.exceptions import AgentRoutingError
from dentalens.infrastructure.llm.prompt_templates import ROUTER_SYSTEM_PROMPT
from dentalens.services.agents.base_agent import AgentContext, AgentResponse, BaseAgent

# Fast-path keyword routing before calling the LLM
_BENEFITS_KEYWORDS = {"covered", "coverage", "plan", "benefit", "deductible", "copay", "premium",
                       "waiting period", "annual maximum", "coinsurance", "ppo", "hmo", "orthodontic",
                       "file a claim", "filing", "how to", "exclusion", "in-network", "out-of-network"}
_CLAIMS_KEYWORDS = {"denied", "approved", "status", "billed", "paid", "anomal",
                     "billing", "fraud", "eob", "appeal", "claim data", "claims data",
                     "approval rate", "claim statistics"}

INTENT_TO_AGENT: dict[IntentType, AgentType] = {
    IntentType.BENEFITS_QUESTION: AgentType.BENEFITS,
    IntentType.CLAIMS_INQUIRY: AgentType.CLAIMS,
}


class RouterAgent(BaseAgent):
    """Triage agent that classifies user intent and routes to specialists.

    Uses a two-tier approach:
    1. Fast keyword heuristic for high-confidence routing
    2. LLM-based classification for ambiguous queries
    """

    def __init__(self, **kwargs):
        super().__init__(
            name="router",
            description="Routes user queries to the appropriate specialist agent",
            **kwargs,
        )

    def _keyword_classify(self, query: str) -> tuple[IntentType, float]:
        """Fast keyword-based intent classification."""
        query_lower = query.lower()
        benefits_score = sum(1 for kw in _BENEFITS_KEYWORDS if kw in query_lower)
        claims_score = sum(1 for kw in _CLAIMS_KEYWORDS if kw in query_lower)

        if benefits_score > 0 and benefits_score > claims_score:
            return IntentType.BENEFITS_QUESTION, min(0.5 + benefits_score * 0.15, 0.95)
        if claims_score > 0 and claims_score > benefits_score:
            return IntentType.CLAIMS_INQUIRY, min(0.5 + claims_score * 0.15, 0.95)
        return IntentType.UNKNOWN, 0.0

    async def _llm_classify(self, query: str) -> tuple[IntentType, float, str]:
        """LLM-based intent classification for ambiguous queries."""
        messages = [
            SystemMessage(content=ROUTER_SYSTEM_PROMPT),
            HumanMessage(content=query),
        ]

        response = await self.llm.ainvoke(messages)
        text = response.content if hasattr(response, "content") else str(response)

        try:
            result = json.loads(text)
            intent = IntentType(result["intent"])
            confidence = float(result["confidence"])
            reasoning = result.get("reasoning", "")
            return intent, confidence, reasoning
        except (json.JSONDecodeError, ValueError, KeyError) as e:
            self.logger.warning("LLM classification parse failed: %s", e)
            return IntentType.GENERAL, 0.5, "Parse error, defaulting to general"

    async def classify(self, query: str) -> tuple[IntentType, float]:
        """Classify user intent using keyword heuristics + LLM fallback."""
        # Try fast path first
        intent, confidence = self._keyword_classify(query)
        if confidence >= ROUTER_CONFIDENCE_THRESHOLD:
            self.logger.info("Keyword routing: %s (confidence=%.2f)", intent.value, confidence)
            return intent, confidence

        # Fall back to LLM classification
        intent, confidence, reasoning = await self._llm_classify(query)
        self.logger.info(
            "LLM routing: %s (confidence=%.2f, reason=%s)",
            intent.value, confidence, reasoning,
        )
        return intent, confidence

    async def process(self, query: str, context: AgentContext) -> AgentResponse:
        """Classify the query. The ConversationManager handles delegation."""
        intent, confidence = await self.classify(query)

        if confidence < ROUTER_CONFIDENCE_THRESHOLD and intent == IntentType.UNKNOWN:
            return AgentResponse(
                content="I can help with dental benefits and claims questions. "
                        "Could you clarify what you'd like to know?",
                agent_name=self.name,
                confidence=confidence,
                metadata={"intent": intent.value, "needs_clarification": True},
            )

        return AgentResponse(
            content="",  # Router doesn't generate content — specialist will
            agent_name=self.name,
            confidence=confidence,
            metadata={"intent": intent.value, "routed_to": INTENT_TO_AGENT.get(intent, AgentType.BENEFITS).value},
        )

    def can_handle(self, intent: IntentType) -> bool:
        return True  # Router handles all intents for classification

    def get_target_agent_type(self, intent: IntentType) -> AgentType:
        """Map an intent to the appropriate specialist agent type."""
        agent_type = INTENT_TO_AGENT.get(intent)
        if agent_type is None:
            raise AgentRoutingError(f"No agent registered for intent: {intent}")
        return agent_type
