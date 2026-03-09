"""ChromaDB vector store wrapper for document storage and similarity search."""

import logging
from pathlib import Path

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings

logger = logging.getLogger("dentalens.vectorstore")


class ChromaVectorStore:
    """Wraps ChromaDB operations behind a clean interface."""

    def __init__(self, persist_dir: Path, embedding_provider: Embeddings):
        self._persist_dir = persist_dir
        self._embedding_provider = embedding_provider
        self._collections: dict[str, Chroma] = {}
        persist_dir.mkdir(parents=True, exist_ok=True)

    def get_or_create_collection(self, name: str) -> Chroma:
        """Get or create a named ChromaDB collection."""
        if name not in self._collections:
            self._collections[name] = Chroma(
                collection_name=name,
                embedding_function=self._embedding_provider,
                persist_directory=str(self._persist_dir / name),
            )
            logger.info("Collection '%s' ready", name)
        return self._collections[name]

    def add_documents(self, collection_name: str, documents: list[Document]) -> int:
        """Add documents to a collection. Returns count of documents added."""
        collection = self.get_or_create_collection(collection_name)
        collection.add_documents(documents)
        logger.info("Added %d documents to '%s'", len(documents), collection_name)
        return len(documents)

    def similarity_search(
        self, collection_name: str, query: str, k: int = 5
    ) -> list[Document]:
        """Search for similar documents in a collection."""
        collection = self.get_or_create_collection(collection_name)
        return collection.similarity_search(query, k=k)

    def similarity_search_with_scores(
        self, collection_name: str, query: str, k: int = 5
    ) -> list[tuple[Document, float]]:
        """Search for similar documents with relevance scores."""
        collection = self.get_or_create_collection(collection_name)
        return collection.similarity_search_with_score(query, k=k)

    def delete_collection(self, name: str) -> None:
        """Delete a collection and remove from cache."""
        if name in self._collections:
            self._collections[name].delete_collection()
            del self._collections[name]
            logger.info("Deleted collection '%s'", name)
