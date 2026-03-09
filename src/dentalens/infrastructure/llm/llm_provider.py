"""Factory for creating LLM instances."""

from langchain_openai import ChatOpenAI
from langchain_core.language_models import BaseChatModel

from dentalens.config.constants import DEFAULT_TEMPERATURE
from dentalens.domain.exceptions import LLMProviderError


class LLMProviderFactory:
    """Creates configured LLM instances (Factory pattern)."""

    @staticmethod
    def create(
        model: str,
        api_key: str,
        temperature: float = DEFAULT_TEMPERATURE,
        streaming: bool = True,
    ) -> BaseChatModel:
        """Create a chat LLM provider.

        Args:
            model: Model name (e.g., 'gpt-4o-mini')
            api_key: OpenAI API key
            temperature: Sampling temperature (lower = more factual)
            streaming: Enable streaming responses

        Returns:
            Configured BaseChatModel instance
        """
        try:
            return ChatOpenAI(
                model=model,
                openai_api_key=api_key,
                temperature=temperature,
                streaming=streaming,
            )
        except Exception as e:
            raise LLMProviderError(f"Failed to create LLM provider '{model}': {e}") from e
