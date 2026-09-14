import asyncio
import sys
import time
from collections import OrderedDict
from typing import Any, Optional, Tuple

from app.cache.cache_backend import BaseCacheBackend


class MemoryCacheBackend(BaseCacheBackend):
    """In-memory cache backend with TTL enforcement and LRU eviction."""

    def __init__(self, max_size: int = 10000, max_memory_bytes: Optional[int] = None):
        self.max_size = max_size
        self.max_memory_bytes = max_memory_bytes
        # Maps key -> (value, expires_at)
        self._store: OrderedDict[str, Tuple[Any, float]] = OrderedDict()
        self._current_memory_bytes: int = 0

    def _evict_lru_if_needed(self) -> None:
        """Evict oldest LRU items if max_size or max_memory_bytes is exceeded."""
        while len(self._store) > self.max_size:
            key, (val, _) = self._store.popitem(last=False)
            if self.max_memory_bytes:
                self._current_memory_bytes -= sys.getsizeof(val) + sys.getsizeof(key)

        if self.max_memory_bytes and self.max_memory_bytes > 0:
            while self._current_memory_bytes > self.max_memory_bytes and self._store:
                key, (val, _) = self._store.popitem(last=False)
                self._current_memory_bytes -= sys.getsizeof(val) + sys.getsizeof(key)

    async def get(self, key: str) -> Optional[Any]:
        if key in self._store:
            value, expires_at = self._store[key]
            if expires_at > time.monotonic():
                self._store.move_to_end(key)
                return value
            else:
                # Expired
                val, _ = self._store.pop(key)
                if self.max_memory_bytes:
                    self._current_memory_bytes -= sys.getsizeof(val) + sys.getsizeof(key)
        return None

    async def set(self, key: str, value: Any, ttl_seconds: int) -> None:
        expires_at = time.monotonic() + ttl_seconds
        if key in self._store:
            old_val, _ = self._store[key]
            if self.max_memory_bytes:
                self._current_memory_bytes -= sys.getsizeof(old_val)
            self._store.move_to_end(key)
        
        self._store[key] = (value, expires_at)
        if self.max_memory_bytes:
            self._current_memory_bytes += sys.getsizeof(value) + sys.getsizeof(key)
        
        self._evict_lru_if_needed()

    async def delete(self, key: str) -> bool:
        if key in self._store:
            val, _ = self._store.pop(key)
            if self.max_memory_bytes:
                self._current_memory_bytes -= sys.getsizeof(val) + sys.getsizeof(key)
            return True
        return False

    async def exists(self, key: str) -> bool:
        if key in self._store:
            _, expires_at = self._store[key]
            if expires_at > time.monotonic():
                return True
            else:
                val, _ = self._store.pop(key)
                if self.max_memory_bytes:
                    self._current_memory_bytes -= sys.getsizeof(val) + sys.getsizeof(key)
        return False

    async def clear(self) -> None:
        self._store.clear()
        self._current_memory_bytes = 0
