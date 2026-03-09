"""Claims analysis agent — analyzes dental claims data for patterns and anomalies."""

from langchain_core.messages import HumanMessage, SystemMessage

from dentalens.domain.enums import IntentType
from dentalens.infrastructure.data.claims_repository import ClaimsRepository
from dentalens.infrastructure.llm.prompt_templates import CLAIMS_ANALYSIS_SYSTEM_PROMPT
from dentalens.services.agents.base_agent import AgentContext, AgentResponse, BaseAgent


class ClaimsAnalysisAgent(BaseAgent):
    """Specialist agent for analyzing dental claims data.

    Queries the claims repository for statistics, anomalies, and trends,
    then uses an LLM to generate natural language analysis.
    """

    def __init__(self, claims_repository: ClaimsRepository, **kwargs):
        super().__init__(
            name="claims",
            description="Analyzes dental claims data for patterns, anomalies, and statistics",
            **kwargs,
        )
        self._claims_repo = claims_repository

    async def process(self, query: str, context: AgentContext) -> AgentResponse:
        """Process a claims inquiry with data-backed analysis."""
        self.logger.info("Processing claims query: %s", query[:100])

        # Gather claims data context
        summary = self._claims_repo.get_claims_summary()
        anomalies = self._claims_repo.detect_anomalies()

        # Build data context for the LLM
        data_context = f"""Claims Summary:
- Total Claims: {summary['total_claims']}
- Total Billed: ${summary['total_billed']:,.2f}
- Total Paid: ${summary['total_paid']:,.2f}
- Average Billed: ${summary['avg_billed']:,.2f}
- Average Paid: ${summary['avg_paid']:,.2f}
- Approval Rate: {summary['approval_rate']:.1%}

Status Breakdown: {summary['status_counts']}
Category Breakdown: {summary['category_counts']}

Anomalous Claims ({len(anomalies)} detected):
"""
        for a in anomalies[:10]:
            data_context += (
                f"- {a['claim_id']}: {a['procedure_code']} billed ${a['billed_amount']:.2f} "
                f"(typical mean ${a['typical_mean']:.2f}, {a['deviation']:.1f} std devs) — {a['reason']}\n"
            )

        # Format history
        history_text = ""
        if context.conversation_history:
            history_text = "\n".join(
                f"{m.role}: {m.content}" for m in context.conversation_history[-6:]
            )

        formatted_prompt = CLAIMS_ANALYSIS_SYSTEM_PROMPT.format(
            context=data_context,
            history=history_text or "No prior conversation.",
        )

        messages = [
            SystemMessage(content=formatted_prompt),
            HumanMessage(content=query),
        ]

        response = await self.llm.ainvoke(messages)
        answer = response.content if hasattr(response, "content") else str(response)

        return AgentResponse(
            content=answer,
            agent_name=self.name,
            metadata={
                "total_claims_analyzed": summary["total_claims"],
                "anomalies_detected": len(anomalies),
            },
        )

    def can_handle(self, intent: IntentType) -> bool:
        return intent == IntentType.CLAIMS_INQUIRY
