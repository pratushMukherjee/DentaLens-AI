"""Benefits Q&A agent — answers dental plan questions using RAG."""

from dentalens.domain.enums import IntentType
from dentalens.infrastructure.llm.prompt_templates import BENEFITS_QA_SYSTEM_PROMPT
from dentalens.services.agents.base_agent import AgentContext, AgentResponse, BaseAgent
from dentalens.services.rag.retrieval_service import RetrievalService


class BenefitsQAAgent(BaseAgent):
    """Specialist agent for answering dental benefit plan questions.

    Uses the RAG pipeline to retrieve relevant plan documents and generate
    accurate, cited answers about coverage, deductibles, and plan details.
    """

    def __init__(self, retrieval_service: RetrievalService, **kwargs):
        super().__init__(
            name="benefits",
            description="Answers questions about dental benefit plans, coverage, and insurance details",
            **kwargs,
        )
        self._retrieval_service = retrieval_service

    async def process(self, query: str, context: AgentContext) -> AgentResponse:
        """Process a benefits question using RAG retrieval."""
        self.logger.info("Processing benefits query: %s", query[:100])

        rag_response = await self._retrieval_service.retrieve_and_generate(
            query=query,
            system_prompt=BENEFITS_QA_SYSTEM_PROMPT,
            conversation_history=context.conversation_history,
        )

        sources = [
            {
                "document": src.source_file,
                "document_type": src.document_type,
                "relevance_score": src.relevance_score,
            }
            for src in rag_response.sources
        ]

        return AgentResponse(
            content=rag_response.answer,
            agent_name=self.name,
            sources=sources,
            confidence=1.0 - (rag_response.sources[0].relevance_score if rag_response.sources else 1.0),
            metadata={"context_chunks_used": len(rag_response.context_used)},
        )

    def can_handle(self, intent: IntentType) -> bool:
        return intent == IntentType.BENEFITS_QUESTION
