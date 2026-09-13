import asyncio
import time
import uuid
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class DLQEntry(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    model: str
    provider_id: str
    error: str
    failed_at: float = Field(default_factory=time.time)
    request_data: Optional[Dict[str, Any]] = None

class DeadLetterQueue:
    """In-memory Dead Letter Queue for capturing permanently failed inference requests."""

    def __init__(self, max_size: int = 1000) -> None:
        self.max_size = max_size
        self._entries: List[DLQEntry] = []
        self._lock = asyncio.Lock()

    async def put(self, entry: DLQEntry) -> None:
        async with self._lock:
            if len(self._entries) >= self.max_size:
                self._entries.pop(0)
            self._entries.append(entry)

    async def get_entries(self, limit: int = 100) -> List[DLQEntry]:
        async with self._lock:
            return list(self._entries[-limit:])

    async def count(self) -> int:
        async with self._lock:
            return len(self._entries)

    async def clear(self) -> None:
        async with self._lock:
            self._entries.clear()
