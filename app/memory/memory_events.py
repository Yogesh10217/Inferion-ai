"""
Memory Lifecycle Event Definitions & Publisher Integration
"""

from typing import Dict, Any, Optional
from datetime import datetime, timezone


class MemoryEventRegistry:
    MEMORY_CREATED = "memory.created"
    MEMORY_UPDATED = "memory.updated"
    MEMORY_RETRIEVED = "memory.retrieved"
    MEMORY_COMPRESSED = "memory.compressed"
    MEMORY_ARCHIVED = "memory.archived"
    MEMORY_EXPIRED = "memory.expired"


class MemoryEventPublisher:
    """Emits memory lifecycle events to event bus."""

    def __init__(self, event_publisher: Optional[Any] = None):
        self.publisher = event_publisher

    async def publish(self, event_type: str, payload: Dict[str, Any]) -> None:
        payload["emitted_at"] = datetime.now(timezone.utc).isoformat()
        if self.publisher and hasattr(self.publisher, "publish"):
            await self.publisher.publish(event_type, payload)
