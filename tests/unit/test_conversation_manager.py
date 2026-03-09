"""Unit tests for Conversation model and memory strategies."""

import pytest

from dentalens.domain.models.conversation import Conversation, Message
from dentalens.services.conversation.memory_strategy import BufferWindowStrategy


def test_conversation_creation():
    conv = Conversation()
    assert conv.conversation_id is not None
    assert len(conv.messages) == 0


def test_add_message():
    conv = Conversation()
    msg = conv.add_message("user", "Hello")
    assert msg.role == "user"
    assert msg.content == "Hello"
    assert len(conv.messages) == 1


def test_get_recent_messages():
    conv = Conversation()
    for i in range(25):
        conv.add_message("user", f"Message {i}")
    recent = conv.get_recent_messages(limit=10)
    assert len(recent) == 10
    assert recent[0].content == "Message 15"
    assert recent[-1].content == "Message 24"


def test_message_agent_source():
    conv = Conversation()
    msg = conv.add_message("assistant", "I can help with that", agent_source="benefits")
    assert msg.agent_source == "benefits"


class TestBufferWindowStrategy:
    @pytest.mark.asyncio
    async def test_returns_recent_messages(self):
        strategy = BufferWindowStrategy(window_size=3)
        messages = [Message(role="user", content=f"msg {i}") for i in range(10)]
        result = await strategy.get_context(messages, max_messages=20)
        assert len(result) == 3
        assert result[0].content == "msg 7"

    @pytest.mark.asyncio
    async def test_fewer_messages_than_window(self):
        strategy = BufferWindowStrategy(window_size=10)
        messages = [Message(role="user", content=f"msg {i}") for i in range(3)]
        result = await strategy.get_context(messages, max_messages=20)
        assert len(result) == 3

    @pytest.mark.asyncio
    async def test_respects_max_messages(self):
        strategy = BufferWindowStrategy(window_size=10)
        messages = [Message(role="user", content=f"msg {i}") for i in range(15)]
        result = await strategy.get_context(messages, max_messages=5)
        assert len(result) == 5
