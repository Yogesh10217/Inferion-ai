import asyncio
import time
from typing import Any, Dict, Optional, Tuple

from app.cache.cache_backend import BaseCacheBackend

class MemoryCacheBackend(BaseCacheBackend):
    """In-memory cache backend with TTL enforcement."""

    def __init__(self):
        # Maps key -> (value, expires_at)
        self._store: Dict[str, Tuple[Any, float]] = {}

    async def get(self, key: str) -> Optional[Any]:
        if key in self._store:
            value, expires_at = self._store[key]
            if expires_at > time.monotonic():
                return value
            else:
                # Expired
                del self._store[key]
        return None

    async def set(self, key: str, value: Any, ttl_seconds: int) -> None:
        expires_at = time.monotonic() + ttl_seconds
        self._store[key] = (value, expires_at)

    async def delete(self, key: str) -> bool:
        if key in self._store:
            del self._store[key]
            return True
        return False

    async def exists(self, key: str) -> bool:
        if key in self._store:
            _, expires_at = self._store[key]
            if expires_at > time.monotonic():
                return True
            else:
                del self._store[key]
        return False

    async def clear(self) -> None:
        self._store.clear()
