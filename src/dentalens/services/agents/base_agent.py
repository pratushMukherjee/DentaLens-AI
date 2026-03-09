"""Abstract base agent defining the Strategy pattern interface for all specialist agents."""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from langchain_core.language_models import BaseChatModel

from dentalens.domain.enums import IntentType


@dataclass
class AgentContext:
    """Context passed to agents for processing."""

    conversation_history: list[Any] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentResponse:
    """Structured response from an agent."""

    content: str
    agent_name: str
    sources: list[dict[str, Any]] = field(default_factory=list)
    confidence: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class BaseAgent(ABC):
    """Abstract base for all specialist agents (Strategy pattern).

    Each agent implements a specific processing strategy for handling
    user queries. The router agent selects the appropriate strategy
    at runtime based on the classified intent.
    """

    def __init__(self, name: str, description: str, llm: BaseChatModel):
        self.name = name
        self.description = description
        self.llm = llm
        self.logger = logging.getLogger(f"dentalens.agent.{name}")

    @abstractmethod
    async def process(self, query: str, context: AgentContext) -> AgentResponse:
        """Process a user query and return a structured response."""
        ...

    @abstractmethod
    def can_handle(self, intent: IntentType) -> bool:
        """Whether this agent handles the given intent type."""
        ...
