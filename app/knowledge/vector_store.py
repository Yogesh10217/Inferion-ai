from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class VectorStore(ABC):
    """Abstract interface for Vector Databases."""

    @abstractmethod
    async def add(self, embeddings: List[Dict[str, Any]], collection_name: str) -> None:
        """Add embeddings to the vector store.

        Args:
            embeddings: List of dictionaries containing 'id', 'vector', and 'metadata'.
            collection_name: Target collection or namespace.
        """

    @abstractmethod
    async def search(
        self,
        query_vector: List[float],
        collection_name: str,
        top_k: int = 10,
        filter_expr: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Search the vector store for similar vectors.

        Args:
            query_vector: The embedding vector to search for.
            collection_name: Target collection or namespace.
            top_k: Number of results to return.
            filter_expr: Metadata filter expression.

        Returns:
            List of dictionaries containing 'id', 'score', and 'metadata'.
        """

    @abstractmethod
    async def delete(self, ids: List[str], collection_name: str) -> None:
        """Delete embeddings from the vector store by ID.

        Args:
            ids: List of IDs to delete.
            collection_name: Target collection or namespace.
        """

    @abstractmethod
    async def update(self, embeddings: List[Dict[str, Any]], collection_name: str) -> None:
        """Update existing embeddings in the vector store.

        Args:
            embeddings: List of dictionaries containing 'id', 'vector', and 'metadata'.
            collection_name: Target collection or namespace.
        """

    @abstractmethod
    async def get(self, ids: List[str], collection_name: str) -> List[Dict[str, Any]]:
        """Retrieve embeddings by ID.

        Args:
            ids: List of IDs to retrieve.
            collection_name: Target collection or namespace.

        Returns:
            List of retrieved embeddings and metadata.
        """

    @abstractmethod
    async def health(self) -> bool:
        """Check the health of the vector store connection.

        Returns:
            True if healthy, False otherwise.
        """
