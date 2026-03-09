"""Dependency injection setup for FastAPI using Depends()."""

from functools import lru_cache
from pathlib import Path

from dentalens.config.settings import Settings
from dentalens.infrastructure.data.claims_repository import ClaimsRepository
from dentalens.infrastructure.llm.llm_provider import LLMProviderFactory
from dentalens.infrastructure.vectorstore.chroma_client import ChromaVectorStore
from dentalens.infrastructure.vectorstore.document_loader import DentalDocumentLoader
from dentalens.infrastructure.vectorstore.embedding_provider import EmbeddingProviderFactory
from dentalens.services.agents.agent_factory import AgentFactory
from dentalens.services.conversation.conversation_manager import ConversationManager
from dentalens.services.evaluation.evaluator import EvaluationPipeline
from dentalens.services.rag.retrieval_service import RetrievalService


@lru_cache
def get_settings() -> Settings:
    """Cached settings instance (singleton)."""
    return Settings()


@lru_cache
def get_vector_store() -> ChromaVectorStore:
    """Cached vector store instance."""
    settings = get_settings()
    embeddings = EmbeddingProviderFactory.create(
        model_name=settings.embedding_model,
        api_key=settings.openai_api_key.get_secret_value(),
    )
    return ChromaVectorStore(
        persist_dir=settings.chroma_persist_dir,
        embedding_provider=embeddings,
    )


@lru_cache
def get_llm():
    """Cached LLM instance."""
    settings = get_settings()
    return LLMProviderFactory.create(
        model=settings.openai_model,
        api_key=settings.openai_api_key.get_secret_value(),
    )


@lru_cache
def get_retrieval_service() -> RetrievalService:
    """Cached retrieval service."""
    return RetrievalService(
        vector_store=get_vector_store(),
        llm=get_llm(),
    )


@lru_cache
def get_claims_repository() -> ClaimsRepository:
    """Cached claims repository."""
    settings = get_settings()
    claims_path = settings.seed_data_dir / "claims" / "synthetic_claims.csv"
    return ClaimsRepository(data_path=claims_path)


@lru_cache
def get_agent_factory() -> AgentFactory:
    """Cached agent factory."""
    return AgentFactory(
        llm=get_llm(),
        retrieval_service=get_retrieval_service(),
        claims_repository=get_claims_repository(),
    )


@lru_cache
def get_conversation_manager() -> ConversationManager:
    """Cached conversation manager."""
    return ConversationManager(agent_factory=get_agent_factory())


@lru_cache
def get_evaluation_pipeline() -> EvaluationPipeline:
    """Cached evaluation pipeline."""
    settings = get_settings()
    eval_llm = LLMProviderFactory.create(
        model=settings.openai_model,
        api_key=settings.openai_api_key.get_secret_value(),
        temperature=0.0,
        streaming=False,
    )
    return EvaluationPipeline(llm=eval_llm)


def get_document_loader() -> DentalDocumentLoader:
    """Document loader (not cached — lightweight)."""
    return DentalDocumentLoader()
