from abc import ABC, abstractmethod
from typing import Any, Optional


class BaseCacheBackend(ABC):
    """Abstract base class for cache backends."""

    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """Retrieve a value by key. Returns None if not found or expired."""

    @abstractmethod
    async def set(self, key: str, value: Any, ttl_seconds: int) -> None:
        """Store a value by key with a TTL in seconds."""

    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete a key from the cache. Returns True if deleted."""

    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Check if a key exists in the cache."""

    @abstractmethod
    async def clear(self) -> None:
        """Clear all entries from the cache."""
