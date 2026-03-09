"""Factory for creating embedding model instances."""

from langchain_openai import OpenAIEmbeddings
from langchain_core.embeddings import Embeddings

from dentalens.domain.exceptions import EmbeddingError


class EmbeddingProviderFactory:
    """Creates embedding model instances based on configuration (Factory pattern)."""

    @staticmethod
    def create(model_name: str, api_key: str) -> Embeddings:
        """Create an embedding provider for the specified model.

        Args:
            model_name: OpenAI embedding model name (e.g., 'text-embedding-3-small')
            api_key: OpenAI API key

        Returns:
            Configured Embeddings instance

        Raises:
            EmbeddingError: If the provider cannot be created
        """
        try:
            return OpenAIEmbeddings(model=model_name, openai_api_key=api_key)
        except Exception as e:
            raise EmbeddingError(f"Failed to create embedding provider '{model_name}': {e}") from e
