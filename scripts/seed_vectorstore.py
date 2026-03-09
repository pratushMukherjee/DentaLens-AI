"""CLI script to ingest dental documents into the ChromaDB vector store."""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from dentalens.config.settings import Settings
from dentalens.config.logging_config import setup_logging
from dentalens.infrastructure.vectorstore.embedding_provider import EmbeddingProviderFactory
from dentalens.infrastructure.vectorstore.chroma_client import ChromaVectorStore
from dentalens.infrastructure.vectorstore.document_loader import DentalDocumentLoader
from dentalens.services.rag.ingestion_service import IngestionService


def main() -> None:
    settings = Settings()
    setup_logging(settings.log_level)

    print("DentaLens AI — Vector Store Seeding")
    print("=" * 40)

    # Create embedding provider
    print(f"Creating embedding provider ({settings.embedding_model})...")
    embeddings = EmbeddingProviderFactory.create(
        model_name=settings.embedding_model,
        api_key=settings.openai_api_key.get_secret_value(),
    )

    # Create vector store
    print(f"Initializing ChromaDB at {settings.chroma_persist_dir}...")
    vector_store = ChromaVectorStore(
        persist_dir=settings.chroma_persist_dir,
        embedding_provider=embeddings,
    )

    # Create document loader and ingestion service
    doc_loader = DentalDocumentLoader()
    ingestion = IngestionService(vector_store, doc_loader)

    # Run ingestion
    print(f"Ingesting documents from {settings.seed_data_dir}...")
    report = ingestion.ingest_all(settings.seed_data_dir)

    print(f"\nIngestion Complete:")
    print(f"  Benefit plan chunks: {report.benefit_plan_chunks}")
    print(f"  FAQ chunks:          {report.faq_chunks}")
    print(f"  Procedure codes:     {report.procedure_code_chunks}")
    print(f"  Total chunks:        {report.total_chunks}")
    if report.errors:
        print(f"  Errors: {len(report.errors)}")
        for err in report.errors:
            print(f"    - {err}")


if __name__ == "__main__":
    main()
