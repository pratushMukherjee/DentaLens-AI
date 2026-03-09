"""Document loading and chunking for dental insurance documents."""

import json
import logging
from pathlib import Path

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from dentalens.config.constants import CHUNK_OVERLAP, CHUNK_SIZE

logger = logging.getLogger("dentalens.document_loader")


class DentalDocumentLoader:
    """Loads and chunks dental insurance documents with metadata preservation."""

    def __init__(self, chunk_size: int = CHUNK_SIZE, chunk_overlap: int = CHUNK_OVERLAP):
        self._splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n## ", "\n### ", "\n- ", "\n\n", "\n", " "],
        )

    def load_benefit_plans(self, dir_path: Path) -> list[Document]:
        """Load and chunk benefit plan markdown documents."""
        documents = []
        for md_file in sorted(dir_path.glob("*.md")):
            text = md_file.read_text(encoding="utf-8")
            # Extract plan ID from content if present
            plan_id = ""
            for line in text.split("\n"):
                if "Plan ID:" in line:
                    plan_id = line.split("Plan ID:")[-1].strip().strip("*")
                    break

            chunks = self._splitter.create_documents(
                texts=[text],
                metadatas=[{
                    "source_file": md_file.name,
                    "document_type": "benefit_plan",
                    "plan_id": plan_id,
                }],
            )
            documents.extend(chunks)
            logger.info("Loaded %d chunks from %s", len(chunks), md_file.name)
        return documents

    def load_faqs(self, dir_path: Path) -> list[Document]:
        """Load and chunk FAQ markdown documents."""
        documents = []
        for md_file in sorted(dir_path.glob("*.md")):
            text = md_file.read_text(encoding="utf-8")
            chunks = self._splitter.create_documents(
                texts=[text],
                metadatas=[{
                    "source_file": md_file.name,
                    "document_type": "faq",
                }],
            )
            documents.extend(chunks)
            logger.info("Loaded %d chunks from %s", len(chunks), md_file.name)
        return documents

    def load_cdt_codes(self, file_path: Path) -> list[Document]:
        """Load CDT procedure codes as individual documents."""
        with open(file_path, encoding="utf-8") as f:
            data = json.load(f)

        documents = []
        for code_entry in data["cdt_codes"]:
            text = (
                f"CDT Code: {code_entry['code']}\n"
                f"Description: {code_entry['description']}\n"
                f"Category: {code_entry['category']}\n"
                f"Typical Cost Range: ${code_entry['typical_cost_range'][0]} - "
                f"${code_entry['typical_cost_range'][1]}\n"
                f"Frequency Limit: {code_entry['frequency_limit']}"
            )
            documents.append(Document(
                page_content=text,
                metadata={
                    "source_file": file_path.name,
                    "document_type": "procedure_code",
                    "cdt_code": code_entry["code"],
                    "category": code_entry["category"],
                },
            ))
        logger.info("Loaded %d CDT code documents from %s", len(documents), file_path.name)
        return documents
