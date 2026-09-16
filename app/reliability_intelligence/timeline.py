"""Chronological timeline for Reliability Intelligence (Phase 5.55)."""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List

logger = logging.getLogger(__name__)


@dataclass
class ReliabilityTimelineEvent:
    event_id: str
    tenant_id: str
    event_type: str
    description: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class ReliabilityTimeline:
    """Tracks chronological lifecycle history."""

    def __init__(self) -> None:
        self._events: Dict[str, List[ReliabilityTimelineEvent]] = {}

    def record_event(self, tenant_id: str, event_type: str, description: str) -> ReliabilityTimelineEvent:
        if tenant_id not in self._events:
            self._events[tenant_id] = []

        ev = ReliabilityTimelineEvent(
            event_id=f"rel_evt_{len(self._events[tenant_id]) + 1}",
            tenant_id=tenant_id,
            event_type=event_type,
            description=description,
        )
        self._events[tenant_id].append(ev)
        return ev

    def get_timeline(self, tenant_id: str) -> List[ReliabilityTimelineEvent]:
        return self._events.get(tenant_id, [])
