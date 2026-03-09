"""Factory for creating configured agent instances with all dependencies."""

from langchain_core.language_models import BaseChatModel

from dentalens.domain.enums import AgentType
from dentalens.infrastructure.data.claims_repository import ClaimsRepository
from dentalens.services.agents.base_agent import BaseAgent
from dentalens.services.agents.benefits_agent import BenefitsQAAgent
from dentalens.services.agents.claims_agent import ClaimsAnalysisAgent
from dentalens.services.agents.router_agent import RouterAgent
from dentalens.services.rag.retrieval_service import RetrievalService


class AgentFactory:
    """Creates fully-configured agent instances (Factory pattern).

    Encapsulates the construction complexity of agents that require
    different combinations of dependencies (LLM, retrieval service,
    claims repository).
    """

    def __init__(
        self,
        llm: BaseChatModel,
        retrieval_service: RetrievalService,
        claims_repository: ClaimsRepository,
    ):
        self._llm = llm
        self._retrieval_service = retrieval_service
        self._claims_repository = claims_repository

    def create(self, agent_type: AgentType) -> BaseAgent:
        """Create an agent instance by type with all required dependencies."""
        match agent_type:
            case AgentType.ROUTER:
                return RouterAgent(llm=self._llm)
            case AgentType.BENEFITS:
                return BenefitsQAAgent(
                    llm=self._llm,
                    retrieval_service=self._retrieval_service,
                )
            case AgentType.CLAIMS:
                return ClaimsAnalysisAgent(
                    llm=self._llm,
                    claims_repository=self._claims_repository,
                )
            case _:
                raise ValueError(f"Unknown agent type: {agent_type}")
