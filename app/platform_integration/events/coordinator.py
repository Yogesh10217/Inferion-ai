"""Cross-Phase Event Coordinator and Subscriber Dispatch (Phase 5.58)."""

import logging
from typing import Dict, Any, List, Callable, Optional
import uuid

from app.platform_integration.models import (
    CrossPhaseEvent,
    CrossPhaseEventType,
    IntegrationPlatform,
    TraceContext,
)
from app.platform_integration.events.events import EventStore

logger = logging.getLogger(__name__)


class EventCoordinator:
    """Publishes and coordinates cross-phase events with subscriber dispatch and audit logging."""

    def __init__(self, store: Optional[EventStore] = None) -> None:
        self.store = store or EventStore()
        self._subscribers: Dict[CrossPhaseEventType, List[Callable[[CrossPhaseEvent], None]]] = {}

    def subscribe(self, event_type: CrossPhaseEventType, callback: Callable[[CrossPhaseEvent], None]) -> None:
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)

    def publish_event(
        self,
        tenant_id: str,
        event_type: CrossPhaseEventType,
        source_platform: IntegrationPlatform,
        payload: Dict[str, Any],
        trace_context: Optional[TraceContext] = None,
        evidence_references: Optional[List[str]] = None,
    ) -> CrossPhaseEvent:
        ctx = trace_context or TraceContext(tenant_id=tenant_id, source_platform=source_platform.value)
        event_id = f"ev-{uuid.uuid4().hex[:12]}"
        event = CrossPhaseEvent(
            event_id=event_id,
            tenant_id=tenant_id,
            event_type=event_type,
            source_platform=source_platform,
            payload=payload,
            trace_context=ctx,
            evidence_references=evidence_references or [],
        )

        # Record into EventStore
        self.store.append(event)
        logger.info(f"Published CrossPhaseEvent: {event.event_id} ({event.event_type.value}) for tenant '{tenant_id}'")

        # Dispatch to registered subscribers
        subscribers = self._subscribers.get(event_type, [])
        for sub in subscribers:
            try:
                sub(event)
            except Exception as e:
                logger.warning(f"Subscriber failed for event {event.event_id}: {e}")

        return event

    def get_events(
        self,
        tenant_id: str,
        event_type: Optional[CrossPhaseEventType] = None,
        platform: Optional[IntegrationPlatform] = None,
    ) -> List[CrossPhaseEvent]:
        return self.store.list_events(tenant_id, event_type, platform)
