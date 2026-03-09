"""Conversation and message domain models."""

from datetime import datetime, timezone
from typing import Any, Literal
from uuid import uuid4

from pydantic import BaseModel, Field


class Message(BaseModel):
    """A single message in a conversation."""

    role: Literal["user", "assistant", "system"]
    content: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = Field(default_factory=dict)
    agent_source: str | None = None


class Conversation(BaseModel):
    """A conversation session containing a sequence of messages."""

    conversation_id: str = Field(default_factory=lambda: str(uuid4()))
    messages: list[Message] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    context: dict[str, Any] = Field(default_factory=dict)

    def add_message(self, role: Literal["user", "assistant", "system"], content: str, **kwargs: Any) -> Message:
        """Add a message to the conversation and return it."""
        msg = Message(role=role, content=content, **kwargs)
        self.messages.append(msg)
        return msg

    def get_recent_messages(self, limit: int = 20) -> list[Message]:
        """Return the most recent messages."""
        return self.messages[-limit:]
