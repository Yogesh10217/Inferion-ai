"""
Memory Embedding Service with Provider Integration & Caching
"""

import math
from typing import Any, Dict, List, Optional


class MemoryEmbeddingService:
    """Generates vector embeddings for semantic and episodic memory items."""

    def __init__(self, provider_factory: Optional[Any] = None):
        self.provider_factory = provider_factory
        self._cache: Dict[str, List[float]] = {}

    async def get_embedding(self, text: str) -> List[float]:
        """Generate text embedding vector."""
        if text in self._cache:
            return self._cache[text]

        if self.provider_factory and hasattr(self.provider_factory, "get_embedding_provider"):
            provider = self.provider_factory.get_embedding_provider()
            vector = await provider.embed(text)
        else:
            # Deterministic float vector embedding fallback
            vector = self._generate_deterministic_vector(text)

        self._cache[text] = vector
        return vector

    async def get_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        return [await self.get_embedding(t) for t in texts]

    def _generate_deterministic_vector(self, text: str, dim: int = 16) -> List[float]:
        """Generates a normalized deterministic vector for similarity search."""
        seed = sum(ord(c) for c in text)
        raw = [math.sin(seed + i) for i in range(dim)]
        norm = math.sqrt(sum(x * x for x in raw)) or 1.0
        return [x / norm for x in raw]
