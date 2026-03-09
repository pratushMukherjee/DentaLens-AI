"""Unit tests for the retrieval service."""

from unittest.mock import MagicMock

import pytest

try:
    from langchain_core.documents import Document
    from dentalens.services.rag.retrieval_service import RetrievalService
    _IMPORTS_AVAILABLE = True
except Exception:
    _IMPORTS_AVAILABLE = False

pytestmark = pytest.mark.skipif(not _IMPORTS_AVAILABLE, reason="ChromaDB incompatible with Python 3.14+")


def test_retrieve_returns_sorted_results():
    mock_vector_store = MagicMock()
    mock_llm = MagicMock()

    mock_vector_store.similarity_search_with_scores.return_value = [
        (Document(page_content="Plan A covers cleanings", metadata={"source_file": "gold.md", "document_type": "benefit_plan"}), 0.3),
        (Document(page_content="Plan B basic info", metadata={"source_file": "silver.md", "document_type": "benefit_plan"}), 0.7),
    ]

    service = RetrievalService(vector_store=mock_vector_store, llm=mock_llm)
    results = service.retrieve("cleanings", collection_names=["benefit_plans"], k=5)

    assert len(results) == 2
    assert results[0].relevance_score < results[1].relevance_score
    assert results[0].source_file == "gold.md"


def test_retrieve_handles_search_failure():
    mock_vector_store = MagicMock()
    mock_llm = MagicMock()

    mock_vector_store.similarity_search_with_scores.side_effect = Exception("Connection failed")

    service = RetrievalService(vector_store=mock_vector_store, llm=mock_llm)
    results = service.retrieve("test query", collection_names=["benefit_plans"])

    assert len(results) == 0
