"""Domain-specific exception hierarchy."""


class DentaLensError(Exception):
    """Base exception for all DentaLens errors."""


class DocumentNotFoundError(DentaLensError):
    """Raised when a requested document cannot be found."""


class AgentRoutingError(DentaLensError):
    """Raised when the router agent cannot determine the correct specialist."""


class EmbeddingError(DentaLensError):
    """Raised when embedding generation fails."""


class LLMProviderError(DentaLensError):
    """Raised when the LLM provider encounters an error."""


class EvaluationError(DentaLensError):
    """Raised when the evaluation pipeline encounters an error."""
