"""
Memory Vector Store & Cosine Similarity Search Engine
"""

import math
from typing import Any, Dict, List, Optional

from app.memory.exceptions import TenantMemoryIsolationError


class MemoryVectorStore:
    """Vector store for indexing memory embeddings with multi-tenant isolation."""

    def __init__(self):
        # memory_id -> {"vector": List[float], "payload": Dict, "organization_id": str, "workspace_id": str}
        self._vectors: Dict[str, Dict[str, Any]] = {}

    def add(
        self,
        memory_id: str,
        vector: List[float],
        payload: Dict[str, Any],
        organization_id: str,
        workspace_id: Optional[str] = None,
    ) -> None:
        if not organization_id:
            raise TenantMemoryIsolationError("organization_id required for vector store insertion")

        self._vectors[memory_id] = {
            "vector": vector,
            "payload": payload,
            "organization_id": organization_id,
            "workspace_id": workspace_id or "default_workspace",
        }

    def update(self, memory_id: str, vector: List[float], payload: Dict[str, Any]) -> None:
        if memory_id in self._vectors:
            self._vectors[memory_id]["vector"] = vector
            self._vectors[memory_id]["payload"] = payload

    def delete(self, memory_id: str) -> bool:
        if memory_id in self._vectors:
            del self._vectors[memory_id]
            return True
        return False

    def similarity_search(
        self,
        query_vector: List[float],
        organization_id: str,
        workspace_id: Optional[str] = None,
        top_k: int = 5,
    ) -> List[Dict[str, Any]]:
        """Cosine similarity vector search with tenant boundary filtering."""
        results = []

        for memory_id, data in self._vectors.items():
            if data["organization_id"] != organization_id:
                continue
            if workspace_id and data["workspace_id"] != workspace_id:
                continue

            sim = self._cosine_similarity(query_vector, data["vector"])
            results.append(
                {
                    "memory_id": memory_id,
                    "score": sim,
                    "payload": data["payload"],
                }
            )

        results.sort(key=lambda item: item["score"], reverse=True)
        return results[:top_k]

    @staticmethod
    def _cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
        if not vec_a or not vec_b or len(vec_a) != len(vec_b):
            return 0.0
        dot = sum(a * b for a, b in zip(vec_a, vec_b))
        norm_a = math.sqrt(sum(a * a for a in vec_a))
        norm_b = math.sqrt(sum(b * b for b in vec_b))
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)
