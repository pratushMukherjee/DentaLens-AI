"""RAG retrieval and response generation service."""

import logging
from dataclasses import dataclass

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage

from dentalens.config.constants import (
    COLLECTION_BENEFIT_PLANS,
    COLLECTION_FAQS,
    COLLECTION_PROCEDURES,
    DEFAULT_RETRIEVAL_K,
)
from dentalens.domain.models.conversation import Message
from dentalens.infrastructure.llm.prompt_templates import BENEFITS_QA_SYSTEM_PROMPT
from dentalens.infrastructure.vectorstore.chroma_client import ChromaVectorStore

logger = logging.getLogger("dentalens.retrieval")

ALL_COLLECTIONS = [COLLECTION_BENEFIT_PLANS, COLLECTION_FAQS, COLLECTION_PROCEDURES]


@dataclass
class RetrievedContext:
    """A piece of retrieved context with metadata."""

    content: str
    source_file: str
    document_type: str
    relevance_score: float


@dataclass
class RAGResponse:
    """Response from the RAG pipeline."""

    answer: str
    sources: list[RetrievedContext]
    context_used: list[str]


class RetrievalService:
    """Retrieves relevant context from the vector store and generates RAG responses."""

    def __init__(self, vector_store: ChromaVectorStore, llm: BaseChatModel):
        self._vector_store = vector_store
        self._llm = llm

    def retrieve(
        self,
        query: str,
        collection_names: list[str] | None = None,
        k: int = DEFAULT_RETRIEVAL_K,
    ) -> list[RetrievedContext]:
        """Retrieve relevant documents across collections.

        Args:
            query: User query to search for
            collection_names: Collections to search (defaults to all)
            k: Number of results per collection
        """
        collections = collection_names or ALL_COLLECTIONS
        results: list[RetrievedContext] = []

        for collection_name in collections:
            try:
                docs_with_scores = self._vector_store.similarity_search_with_scores(
                    collection_name, query, k=k
                )
                for doc, score in docs_with_scores:
                    results.append(RetrievedContext(
                        content=doc.page_content,
                        source_file=doc.metadata.get("source_file", "unknown"),
                        document_type=doc.metadata.get("document_type", "unknown"),
                        relevance_score=float(score),
                    ))
            except Exception as e:
                logger.warning("Search failed for collection '%s': %s", collection_name, e)

        # Sort by relevance (lower distance = more relevant for ChromaDB)
        results.sort(key=lambda r: r.relevance_score)
        return results[:k]

    async def retrieve_and_generate(
        self,
        query: str,
        system_prompt: str = BENEFITS_QA_SYSTEM_PROMPT,
        conversation_history: list[Message] | None = None,
        collection_names: list[str] | None = None,
    ) -> RAGResponse:
        """Full RAG pipeline: retrieve context, augment prompt, generate response.

        Args:
            query: User question
            system_prompt: System prompt template with {context} and {history} placeholders
            conversation_history: Prior conversation messages for context
            collection_names: Which collections to search
        """
        # Retrieve relevant context
        retrieved = self.retrieve(query, collection_names)
        context_text = "\n\n---\n\n".join(r.content for r in retrieved)

        # Format conversation history
        history_text = ""
        if conversation_history:
            history_text = "\n".join(
                f"{m.role}: {m.content}" for m in conversation_history[-6:]
            )

        # Build the augmented prompt
        formatted_system = system_prompt.format(
            context=context_text or "No relevant context found.",
            history=history_text or "No prior conversation.",
        )

        messages = [
            SystemMessage(content=formatted_system),
            HumanMessage(content=query),
        ]

        # Generate response
        response = await self._llm.ainvoke(messages)
        answer = response.content if hasattr(response, "content") else str(response)

        return RAGResponse(
            answer=answer,
            sources=retrieved,
            context_used=[r.content for r in retrieved],
        )
