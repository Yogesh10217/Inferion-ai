"""
Multi-Strategy Memory Retrieval Engine
"""

from typing import Any, Dict, List, Optional

from app.memory.memory_embeddings import MemoryEmbeddingService
from app.memory.memory_ranker import MemoryRanker
from app.memory.memory_vector_store import MemoryVectorStore


class MemoryRetriever:
    """Executes multi-strategy retrieval across memory records."""

    def __init__(
        self,
        vector_store: Optional[MemoryVectorStore] = None,
        embedding_service: Optional[MemoryEmbeddingService] = None,
        ranker: Optional[MemoryRanker] = None,
    ):
        self.vector_store = vector_store or MemoryVectorStore()
        self.embedding_service = embedding_service or MemoryEmbeddingService()
        self.ranker = ranker or MemoryRanker()

    async def retrieve_semantic(
        self,
        query: str,
        organization_id: str,
        workspace_id: Optional[str] = None,
        top_k: int = 5,
    ) -> List[Dict[str, Any]]:
        query_vector = await self.embedding_service.get_embedding(query)
        matches = self.vector_store.similarity_search(
            query_vector=query_vector,
            organization_id=organization_id,
            workspace_id=workspace_id,
            top_k=top_k,
        )

        candidates = []
        for m in matches:
            payload = m["payload"]
            candidates.append({
                "memory_id": m["memory_id"],
                "content": payload.get("content", ""),
                "similarity_score": m["score"],
                "recency_score": 0.8,
                "importance_score": payload.get("importance_score", 0.5),
                "confidence_score": payload.get("confidence_score", 0.9),
                "payload": payload,
            })

        return self.ranker.rank(candidates)
