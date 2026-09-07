"""Unified Intelligence Chronological Timeline Engine for Phase 5.51 Enterprise AI Unified Intelligence."""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.unified_intelligence.domains import IntelligenceDomain


class TimelineEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: f"time-evt-{uuid.uuid4().hex[:8]}")
    correlation_id: str = Field(default_factory=lambda: f"corr-{uuid.uuid4().hex[:8]}")
    tenant_id: str
    domain: IntelligenceDomain
    event_type: str
    summary: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class UnifiedTimeline(BaseModel):
    timeline_id: str = Field(default_factory=lambda: f"timeline-{uuid.uuid4().hex[:8]}")
    tenant_id: str
    events: List[TimelineEvent] = Field(default_factory=list)


# Alias for backward compatibility
CorrelationTimeline = UnifiedTimeline


class UnifiedTimelineEngine:
    """Combines chronological events from Security, Identity, Operations, Policy, Knowledge, and Decisions."""

    def __init__(self) -> None:
        self._events: Dict[str, List[TimelineEvent]] = {}

    def record_event(
        self,
        tenant_id: str,
        domain: IntelligenceDomain,
        event_type: str,
        summary: str,
        correlation_id: Optional[str] = None,
    ) -> TimelineEvent:
        evt = TimelineEvent(
            correlation_id=correlation_id or f"corr-{uuid.uuid4().hex[:8]}",
            tenant_id=tenant_id,
            domain=domain,
            event_type=event_type,
            summary=summary,
        )
        self._events.setdefault(tenant_id, []).append(evt)
        return evt

    def get_timeline(self, tenant_id: str) -> UnifiedTimeline:
        events = self._events.get(tenant_id, [])
        sorted_events = sorted(events, key=lambda e: e.timestamp)
        return UnifiedTimeline(tenant_id=tenant_id, events=sorted_events)
