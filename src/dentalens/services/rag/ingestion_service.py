"""Document ingestion pipeline for the RAG system."""

import logging
from dataclasses import dataclass, field
from pathlib import Path

from dentalens.config.constants import (
    COLLECTION_BENEFIT_PLANS,
    COLLECTION_FAQS,
    COLLECTION_PROCEDURES,
)
from dentalens.infrastructure.vectorstore.chroma_client import ChromaVectorStore
from dentalens.infrastructure.vectorstore.document_loader import DentalDocumentLoader

logger = logging.getLogger("dentalens.ingestion")


@dataclass
class IngestionReport:
    """Summary of a document ingestion run."""

    benefit_plan_chunks: int = 0
    faq_chunks: int = 0
    procedure_code_chunks: int = 0
    errors: list[str] = field(default_factory=list)

    @property
    def total_chunks(self) -> int:
        return self.benefit_plan_chunks + self.faq_chunks + self.procedure_code_chunks


class IngestionService:
    """Orchestrates document ingestion into the vector store."""

    def __init__(
        self,
        vector_store: ChromaVectorStore,
        document_loader: DentalDocumentLoader,
    ):
        self._vector_store = vector_store
        self._document_loader = document_loader

    def ingest_all(self, data_dir: Path) -> IngestionReport:
        """Ingest all seed documents into the vector store.

        Args:
            data_dir: Root directory containing benefit_plans/, faqs/, procedures/

        Returns:
            IngestionReport with chunk counts and any errors
        """
        report = IngestionReport()

        # Ingest benefit plans
        plans_dir = data_dir / "benefit_plans"
        if plans_dir.exists():
            try:
                docs = self._document_loader.load_benefit_plans(plans_dir)
                report.benefit_plan_chunks = self._vector_store.add_documents(
                    COLLECTION_BENEFIT_PLANS, docs
                )
            except Exception as e:
                report.errors.append(f"Benefit plans ingestion failed: {e}")
                logger.error("Benefit plans ingestion failed: %s", e)

        # Ingest FAQs
        faqs_dir = data_dir / "faqs"
        if faqs_dir.exists():
            try:
                docs = self._document_loader.load_faqs(faqs_dir)
                report.faq_chunks = self._vector_store.add_documents(
                    COLLECTION_FAQS, docs
                )
            except Exception as e:
                report.errors.append(f"FAQ ingestion failed: {e}")
                logger.error("FAQ ingestion failed: %s", e)

        # Ingest CDT procedure codes
        procedures_file = data_dir / "procedures" / "cdt_codes.json"
        if procedures_file.exists():
            try:
                docs = self._document_loader.load_cdt_codes(procedures_file)
                report.procedure_code_chunks = self._vector_store.add_documents(
                    COLLECTION_PROCEDURES, docs
                )
            except Exception as e:
                report.errors.append(f"Procedure codes ingestion failed: {e}")
                logger.error("Procedure codes ingestion failed: %s", e)

        logger.info(
            "Ingestion complete: %d total chunks (%d plans, %d FAQs, %d procedures), %d errors",
            report.total_chunks,
            report.benefit_plan_chunks,
            report.faq_chunks,
            report.procedure_code_chunks,
            len(report.errors),
        )
        return report
