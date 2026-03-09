"""Integration tests for the RAG pipeline (document loading and ingestion)."""

from pathlib import Path

import pytest

try:
    from dentalens.infrastructure.vectorstore.document_loader import DentalDocumentLoader
    _IMPORTS_AVAILABLE = True
except Exception:
    _IMPORTS_AVAILABLE = False

pytestmark = pytest.mark.skipif(not _IMPORTS_AVAILABLE, reason="ChromaDB incompatible with Python 3.14+")


@pytest.fixture
def loader():
    return DentalDocumentLoader(chunk_size=200, chunk_overlap=20)


def test_load_benefit_plans(loader):
    plans_dir = Path("data/seed/benefit_plans")
    if not plans_dir.exists():
        pytest.skip("Seed data not available")

    docs = loader.load_benefit_plans(plans_dir)
    assert len(docs) > 0

    # Check metadata
    for doc in docs:
        assert "source_file" in doc.metadata
        assert doc.metadata["document_type"] == "benefit_plan"
        assert doc.page_content  # Not empty


def test_load_faqs(loader):
    faqs_dir = Path("data/seed/faqs")
    if not faqs_dir.exists():
        pytest.skip("Seed data not available")

    docs = loader.load_faqs(faqs_dir)
    assert len(docs) > 0

    for doc in docs:
        assert doc.metadata["document_type"] == "faq"


def test_load_cdt_codes(loader):
    codes_path = Path("data/seed/procedures/cdt_codes.json")
    if not codes_path.exists():
        pytest.skip("Seed data not available")

    docs = loader.load_cdt_codes(codes_path)
    assert len(docs) == 27  # Number of CDT codes in our file

    # Check a specific code
    d1110_docs = [d for d in docs if d.metadata.get("cdt_code") == "D1110"]
    assert len(d1110_docs) == 1
    assert "prophylaxis" in d1110_docs[0].page_content.lower()


def test_chunking_produces_reasonable_sizes(loader):
    plans_dir = Path("data/seed/benefit_plans")
    if not plans_dir.exists():
        pytest.skip("Seed data not available")

    docs = loader.load_benefit_plans(plans_dir)
    for doc in docs:
        # Chunks should be reasonable size (with some tolerance for boundary effects)
        assert len(doc.page_content) <= 300  # chunk_size=200 + some tolerance
