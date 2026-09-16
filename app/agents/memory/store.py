"""
Pluggable Memory Storage Backend
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class IMemoryStore(ABC):
    @abstractmethod
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        pass

    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        pass

    @abstractmethod
    async def delete(self, key: str) -> None:
        pass


class InMemoryStore(IMemoryStore):
    def __init__(self):
        self._data: Dict[str, Any] = {}

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        self._data[key] = value

    async def get(self, key: str) -> Optional[Any]:
        return self._data.get(key)

    async def delete(self, key: str) -> None:
        self._data.pop(key, None)
