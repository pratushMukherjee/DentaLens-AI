"""Memory strategies for conversation context management (Strategy pattern)."""

from abc import ABC, abstractmethod

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage

from dentalens.config.constants import BUFFER_WINDOW_SIZE
from dentalens.domain.models.conversation import Message


class MemoryStrategy(ABC):
    """Abstract strategy for selecting which messages to include in LLM context."""

    @abstractmethod
    async def get_context(self, messages: list[Message], max_messages: int) -> list[Message]:
        """Select messages to include in the context window."""
        ...


class BufferWindowStrategy(MemoryStrategy):
    """Returns the most recent N messages (simple sliding window)."""

    def __init__(self, window_size: int = BUFFER_WINDOW_SIZE):
        self._window_size = window_size

    async def get_context(self, messages: list[Message], max_messages: int) -> list[Message]:
        limit = min(self._window_size, max_messages)
        return messages[-limit:]


class SummaryStrategy(MemoryStrategy):
    """Summarizes older messages while keeping recent ones verbatim.

    Keeps the last `recent_count` messages as-is and summarizes
    everything before them into a single system message.
    """

    def __init__(self, llm: BaseChatModel, recent_count: int = 4):
        self._llm = llm
        self._recent_count = recent_count

    async def get_context(self, messages: list[Message], max_messages: int) -> list[Message]:
        if len(messages) <= self._recent_count:
            return messages

        older = messages[:-self._recent_count]
        recent = messages[-self._recent_count:]

        # Summarize older messages
        summary_prompt = (
            "Summarize the following conversation history in 2-3 sentences, "
            "focusing on key topics discussed and any important context:\n\n"
        )
        for msg in older:
            summary_prompt += f"{msg.role}: {msg.content}\n"

        response = await self._llm.ainvoke([
            SystemMessage(content="You are a concise conversation summarizer."),
            HumanMessage(content=summary_prompt),
        ])

        summary_text = response.content if hasattr(response, "content") else str(response)
        summary_message = Message(
            role="system",
            content=f"Previous conversation summary: {summary_text}",
        )

        return [summary_message] + recent
