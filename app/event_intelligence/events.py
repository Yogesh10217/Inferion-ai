"""Enterprise Event Model Subsystem (Phase 5.34)."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.event_intelligence.exceptions import CrossTenantEventAccessException, EventNotFoundException
from app.platform_contracts.redaction import SensitiveDataSanitizer


class EventCategory(str, Enum):
    OPERATIONAL = "OPERATIONAL"
    SECURITY = "SECURITY"
    COMPLIANCE = "COMPLIANCE"
    DATA_GOVERNANCE = "DATA_GOVERNANCE"
    ARCHITECTURE = "ARCHITECTURE"
    AI_LIFECYCLE = "AI_LIFECYCLE"
    PORTFOLIO = "PORTFOLIO"
    DECISION = "DECISION"
    FINANCIAL = "FINANCIAL"
    APPLICATION = "APPLICATION"
    DEVELOPER = "DEVELOPER"
    CUSTOM = "CUSTOM"


class EventType(str, Enum):
    INCIDENT_RAISED = "INCIDENT_RAISED"
    SECURITY_THREAT_DETECTED = "SECURITY_THREAT_DETECTED"
    VULNERABILITY_FOUND = "VULNERABILITY_FOUND"
    DATA_DRIFT_DETECTED = "DATA_DRIFT_DETECTED"
    MODEL_PROMOTED = "MODEL_PROMOTED"
    COMPLIANCE_VIOLATION = "COMPLIANCE_VIOLATION"
    ARCHITECTURE_DRIFT = "ARCHITECTURE_DRIFT"
    COST_ANOMALY = "COST_ANOMALY"
    DEPLOYMENT_EXECUTED = "DEPLOYMENT_EXECUTED"
    CUSTOM_EVENT = "CUSTOM_EVENT"


class EventSeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class EventPriority(str, Enum):
    P4_LOW = "P4_LOW"
    P3_MEDIUM = "P3_MEDIUM"
    P2_HIGH = "P2_HIGH"
    P1_CRITICAL = "P1_CRITICAL"


class EventStatus(str, Enum):
    RECEIVED = "RECEIVED"
    NORMALIZED = "NORMALIZED"
    CLASSIFIED = "CLASSIFIED"
    CORRELATED = "CORRELATED"
    AUTOMATED = "AUTOMATED"
    RESOLVED = "RESOLVED"


class EventSource(BaseModel):
    source_id: str
    source_name: str
    subsystem: str = "GENERIC"


class EventMetadata(BaseModel):
    payload: Dict[str, Any] = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)


class EventReference(BaseModel):
    reference_id: str
    reference_type: str


class EnterpriseEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: f"evt_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    source: EventSource
    event_type: EventType = EventType.CUSTOM_EVENT
    category: EventCategory = EventCategory.OPERATIONAL
    severity: EventSeverity = EventSeverity.MEDIUM
    priority: EventPriority = EventPriority.P3_MEDIUM
    status: EventStatus = EventStatus.RECEIVED
    metadata: EventMetadata = Field(default_factory=EventMetadata)
    correlation_reference: Optional[str] = None
    idempotency_reference: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class EventManager:
    """Manages creation, retrieval, and sanitization of Enterprise Events."""

    def __init__(self) -> None:
        self.sanitizer = SensitiveDataSanitizer()
        self._events: Dict[str, EnterpriseEvent] = {}

    def create_event(
        self,
        tenant_id: str,
        source_id: str,
        source_name: str,
        event_type: EventType = EventType.CUSTOM_EVENT,
        category: EventCategory = EventCategory.OPERATIONAL,
        severity: EventSeverity = EventSeverity.MEDIUM,
        payload: Optional[Dict[str, Any]] = None,
        idempotency_reference: Optional[str] = None,
    ) -> EnterpriseEvent:
        sanitized_payload = self.sanitizer.sanitize_copy(payload or {})
        evt = EnterpriseEvent(
            tenant_id=tenant_id,
            source=EventSource(source_id=source_id, source_name=source_name),
            event_type=event_type,
            category=category,
            severity=severity,
            metadata=EventMetadata(payload=sanitized_payload),
            idempotency_reference=idempotency_reference,
        )
        self._events[evt.event_id] = evt
        return evt

    def ingest_event(
        self,
        tenant_id: str,
        title: str,
        source_system: str = "GENERIC",
        payload: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> EnterpriseEvent:
        return self.create_event(
            tenant_id=tenant_id,
            source_id=f"src_{uuid.uuid4().hex[:8]}",
            source_name=source_system,
            payload={"title": title, **(payload or {})},
        )

    def get_event(self, event_id: str, tenant_id: str) -> EnterpriseEvent:
        evt = self._events.get(event_id)
        if not evt:
            raise EventNotFoundException(event_id)
        if tenant_id != "global" and evt.tenant_id != "global" and tenant_id != evt.tenant_id:
            raise CrossTenantEventAccessException(tenant_id, evt.tenant_id)
        return evt

    def list_events(self, tenant_id: str) -> List[EnterpriseEvent]:
        return [e for e in self._events.values() if e.tenant_id == tenant_id]
