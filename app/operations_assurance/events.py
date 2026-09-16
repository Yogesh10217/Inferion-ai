"""Operational event intelligence integrating with platform event primitives without duplicating ingestion engines."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.event_intelligence.manager import EventIntelligenceManager
from app.operations_assurance.exceptions import (
    CrossTenantOperationsAssuranceException,
    OperationalEventNotFoundException,
)


class OperationalEventType(str, Enum):
    SERVICE_DEGRADATION = "SERVICE_DEGRADATION"
    ERROR_SPIKE = "ERROR_SPIKE"
    LATENCY_SPIKE = "LATENCY_SPIKE"
    CAPACITY_EXHAUSTION = "CAPACITY_EXHAUSTION"
    DEPENDENCY_FAILURE = "DEPENDENCY_FAILURE"
    CONFIGURATION_CHANGE = "CONFIGURATION_CHANGE"
    INFRASTRUCTURE_ALERT = "INFRASTRUCTURE_ALERT"


class OperationalSeverity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class OperationalEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    service_id: str
    event_type: OperationalEventType
    severity: OperationalSeverity = OperationalSeverity.WARNING
    summary: str
    payload: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class OperationalEventManager:
    """Manages operational event intelligence using platform event capabilities."""

    def __init__(self, event_intelligence_manager: Optional[EventIntelligenceManager] = None) -> None:
        self.event_intelligence_manager = event_intelligence_manager or EventIntelligenceManager()
        self._events: Dict[str, Dict[str, OperationalEvent]] = {}  # tenant_id -> {event_id: event}

    def record_event(
        self,
        tenant_id: str,
        service_id: str,
        event_type: OperationalEventType,
        summary: str,
        severity: OperationalSeverity = OperationalSeverity.WARNING,
        payload: Optional[Dict[str, Any]] = None,
    ) -> OperationalEvent:
        event = OperationalEvent(
            tenant_id=tenant_id,
            service_id=service_id,
            event_type=event_type,
            severity=severity,
            summary=summary,
            payload=payload or {},
        )
        if tenant_id not in self._events:
            self._events[tenant_id] = {}
        self._events[tenant_id][event.event_id] = event
        return event

    def list_events_for_service(self, tenant_id: str, service_id: str) -> List[OperationalEvent]:
        tenant_events = self._events.get(tenant_id, {})
        return [evt for evt in tenant_events.values() if evt.service_id == service_id]

    def get_event(self, tenant_id: str, event_id: str) -> OperationalEvent:
        if tenant_id not in self._events or event_id not in self._events[tenant_id]:
            for tid, evts in self._events.items():
                if tid != tenant_id and event_id in evts:
                    raise CrossTenantOperationsAssuranceException("Access denied.")
            raise OperationalEventNotFoundException("Operational event not found.")
        return self._events[tenant_id][event_id]
