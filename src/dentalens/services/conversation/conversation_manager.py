"""Conversation manager — orchestrates multi-agent chat with memory."""

import logging
from collections.abc import AsyncGenerator

from dentalens.domain.enums import AgentType, IntentType
from dentalens.domain.models.conversation import Conversation, Message
from dentalens.services.agents.agent_factory import AgentFactory
from dentalens.services.agents.agent_registry import AgentRegistry
from dentalens.services.agents.base_agent import AgentContext
from dentalens.services.agents.router_agent import RouterAgent
from dentalens.services.conversation.memory_strategy import BufferWindowStrategy, MemoryStrategy

logger = logging.getLogger("dentalens.conversation")


class ConversationManager:
    """Manages conversation state and orchestrates agent interactions.

    Coordinates the router agent, specialist agents, and conversation
    memory to produce coherent multi-turn conversations.
    """

    def __init__(
        self,
        agent_factory: AgentFactory,
        memory_strategy: MemoryStrategy | None = None,
    ):
        self._conversations: dict[str, Conversation] = {}
        self._agent_factory = agent_factory
        self._memory_strategy = memory_strategy or BufferWindowStrategy()

        # Build agent registry
        self._registry = AgentRegistry()
        self._router = agent_factory.create(AgentType.ROUTER)
        self._registry.register(AgentType.ROUTER, self._router)
        self._registry.register(AgentType.BENEFITS, agent_factory.create(AgentType.BENEFITS))
        self._registry.register(AgentType.CLAIMS, agent_factory.create(AgentType.CLAIMS))

    def create_conversation(self) -> Conversation:
        """Create a new conversation session."""
        conv = Conversation()
        self._conversations[conv.conversation_id] = conv
        logger.info("Created conversation %s", conv.conversation_id)
        return conv

    def get_conversation(self, conversation_id: str) -> Conversation | None:
        return self._conversations.get(conversation_id)

    def get_or_create_conversation(self, conversation_id: str | None = None) -> Conversation:
        if conversation_id and conversation_id in self._conversations:
            return self._conversations[conversation_id]
        return self.create_conversation()

    async def chat(self, conversation_id: str | None, user_message: str) -> tuple[str, str, dict]:
        """Process a user message and return the response.

        Args:
            conversation_id: Existing conversation ID or None for new
            user_message: The user's message text

        Returns:
            Tuple of (response_text, conversation_id, metadata)
        """
        conv = self.get_or_create_conversation(conversation_id)
        conv.add_message("user", user_message)

        # Get conversation context via memory strategy
        context_messages = await self._memory_strategy.get_context(
            conv.messages, max_messages=20
        )
        agent_context = AgentContext(conversation_history=context_messages)

        # Route the query
        assert isinstance(self._router, RouterAgent)
        intent, confidence = await self._router.classify(user_message)

        # Handle low-confidence / general queries
        if intent in (IntentType.GENERAL, IntentType.UNKNOWN):
            response_text = (
                "I'm DentaLens AI, your dental insurance assistant. I can help with:\n\n"
                "- **Benefits questions** — coverage details, plan comparisons, deductibles\n"
                "- **Claims inquiries** — claim status, billing analysis, anomaly detection\n\n"
                "What would you like to know?"
            )
            conv.add_message("assistant", response_text, agent_source="router")
            return response_text, conv.conversation_id, {"agent": "router", "intent": intent.value}

        # Delegate to specialist agent
        target_type = self._router.get_target_agent_type(intent)
        specialist = self._registry.get(target_type)
        response = await specialist.process(user_message, agent_context)

        conv.add_message("assistant", response.content, agent_source=response.agent_name)

        metadata = {
            "agent": response.agent_name,
            "intent": intent.value,
            "confidence": confidence,
            "sources": response.sources,
            **response.metadata,
        }

        return response.content, conv.conversation_id, metadata

    async def chat_stream(
        self, conversation_id: str | None, user_message: str
    ) -> AsyncGenerator[str, None]:
        """Stream a chat response token by token.

        Yields response text chunks as they become available.
        """
        # For streaming, we use the same routing but stream the specialist response
        response_text, conv_id, metadata = await self.chat(conversation_id, user_message)

        # Simulate streaming by yielding chunks
        # In production, this would use the LLM's streaming interface
        chunk_size = 20
        for i in range(0, len(response_text), chunk_size):
            yield response_text[i:i + chunk_size]
