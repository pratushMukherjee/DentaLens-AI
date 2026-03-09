"""Chat endpoints — conversational AI with multi-agent routing."""

from fastapi import APIRouter, Depends

from dentalens.api.dependencies import get_conversation_manager
from dentalens.api.schemas.requests import ChatRequest
from dentalens.api.schemas.responses import ChatResponse, SourceReference
from dentalens.services.conversation.conversation_manager import ConversationManager

router = APIRouter(prefix="/api/v1/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    manager: ConversationManager = Depends(get_conversation_manager),
) -> ChatResponse:
    """Process a chat message with automatic agent routing."""
    response_text, conversation_id, metadata = await manager.chat(
        conversation_id=request.conversation_id,
        user_message=request.message,
    )

    sources = [
        SourceReference(
            document=s.get("document", ""),
            document_type=s.get("document_type"),
            relevance_score=s.get("relevance_score"),
        )
        for s in metadata.get("sources", [])
    ]

    return ChatResponse(
        conversation_id=conversation_id,
        response=response_text,
        agent_used=metadata.get("agent", "unknown"),
        sources=sources,
        confidence=metadata.get("confidence"),
        metadata={k: v for k, v in metadata.items() if k not in ("sources", "agent", "confidence")},
    )


@router.get("/history/{conversation_id}")
async def get_history(
    conversation_id: str,
    manager: ConversationManager = Depends(get_conversation_manager),
) -> dict:
    """Get conversation history."""
    conv = manager.get_conversation(conversation_id)
    if conv is None:
        return {"conversation_id": conversation_id, "messages": []}

    return {
        "conversation_id": conversation_id,
        "messages": [
            {
                "role": m.role,
                "content": m.content,
                "timestamp": m.timestamp.isoformat(),
                "agent_source": m.agent_source,
            }
            for m in conv.messages
        ],
    }
