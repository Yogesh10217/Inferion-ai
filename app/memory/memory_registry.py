"""
Memory Provider & Store Registry
"""

from typing import Dict

from app.memory.memory_store import MemoryStore
from app.memory.memory_vector_store import MemoryVectorStore


class MemoryRegistry:
    """Registry managing active memory stores, vector databases, and provider backends."""

    def __init__(self):
        self._memory_stores: Dict[str, MemoryStore] = {}
        self._vector_stores: Dict[str, MemoryVectorStore] = {}
        self._default_store = MemoryStore()
        self._default_vector_store = MemoryVectorStore()

    def get_store(self, name: str = "default") -> MemoryStore:
        if name == "default":
            return self._default_store
        return self._memory_stores.get(name, self._default_store)

    def get_vector_store(self, name: str = "default") -> MemoryVectorStore:
        if name == "default":
            return self._default_vector_store
        return self._vector_stores.get(name, self._default_vector_store)

    def register_store(self, name: str, store: MemoryStore) -> None:
        self._memory_stores[name] = store

    def register_vector_store(self, name: str, vector_store: MemoryVectorStore) -> None:
        self._vector_stores[name] = vector_store
