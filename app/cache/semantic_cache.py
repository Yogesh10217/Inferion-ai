"""
Semantic / Vector Cache Module.

Computes text embeddings for prompt similarity matching to return cached responses
when prompt similarity exceeds threshold (default: 0.95).
"""

from typing import List, Optional, Tuple
import math
import time

from app.schemas.inference_response import InferenceResponse


def _dummy_embed(text: str) -> List[float]:
    """Generates a simple deterministic mock vector embedding from text string."""
    vec = [0.0] * 64
    for i, char in enumerate(text[:64]):
        vec[i % 64] += ord(char) / 255.0
    norm = math.sqrt(sum(v * v for v in vec)) or 1.0
    return [v / norm for v in vec]


def _cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    if len(vec1) != len(vec2) or not vec1:
        return 0.0
    dot = sum(a * b for a, b in zip(vec1, vec2))
    norm1 = math.sqrt(sum(a * a for a in vec1))
    norm2 = math.sqrt(sum(b * b for b in vec2))
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return dot / (norm1 * norm2)


class SemanticCacheEntry:
    def __init__(self, prompt: str, embedding: List[float], response: InferenceResponse, model_id: str):
        self.prompt = prompt
        self.embedding = embedding
        self.response = response
        self.model_id = model_id
        self.created_at = time.time()


class SemanticCache:
    """Semantic vector cache supporting prompt similarity lookup."""

    def __init__(self, similarity_threshold: float = 0.95, max_entries: int = 1000):
        self.similarity_threshold = similarity_threshold
        self.max_entries = max_entries
        self._entries: List[SemanticCacheEntry] = []

    def get(self, prompt: str, model_id: str) -> Optional[Tuple[InferenceResponse, float]]:
        """Query semantic cache for nearest prompt match. Returns (response, similarity) if >= threshold."""
        query_vec = _dummy_embed(prompt)
        best_entry: Optional[SemanticCacheEntry] = None
        best_sim = 0.0

        for entry in self._entries:
            if entry.model_id != model_id:
                continue
            sim = _cosine_similarity(query_vec, entry.embedding)
            if sim > best_sim:
                best_sim = sim
                best_entry = entry

        if best_entry and best_sim >= self.similarity_threshold:
            resp = best_entry.response
            return resp, best_sim
        return None

    def put(self, prompt: str, model_id: str, response: InferenceResponse) -> None:
        """Store prompt vector and response in semantic cache."""
        if len(self._entries) >= self.max_entries:
            self._entries.pop(0)

        vec = _dummy_embed(prompt)
        self._entries.append(SemanticCacheEntry(prompt=prompt, embedding=vec, response=response, model_id=model_id))

    def clear(self) -> None:
        self._entries.clear()

    def size(self) -> int:
        return len(self._entries)
