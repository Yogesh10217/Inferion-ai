"""Cross-Phase Event Data Structures and Store (Phase 5.58)."""

from typing import Dict, List, Optional

from app.platform_integration.models import (
    CrossPhaseEvent,
    CrossPhaseEventType,
    IntegrationPlatform,
)


class EventStore:
    """In-memory thread-safe event storage partitioned by tenant."""

    def __init__(self) -> None:
        self._events: Dict[str, List[CrossPhaseEvent]] = {}

    def append(self, event: CrossPhaseEvent) -> None:
        tid = event.tenant_id
        if tid not in self._events:
            self._events[tid] = []
        self._events[tid].append(event)

    def list_events(
        self,
        tenant_id: str,
        event_type: Optional[CrossPhaseEventType] = None,
        platform: Optional[IntegrationPlatform] = None,
    ) -> List[CrossPhaseEvent]:
        tenant_events = self._events.get(tenant_id, [])
        filtered = tenant_events
        if event_type:
            filtered = [e for e in filtered if e.event_type == event_type]
        if platform:
            filtered = [e for e in filtered if e.source_platform == platform]
        return list(filtered)

    def count_events(self, tenant_id: str) -> int:
        return len(self._events.get(tenant_id, []))
