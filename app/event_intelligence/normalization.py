"""Event Normalization Subsystem (Phase 5.34)."""

from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.event_intelligence.events import EnterpriseEvent, EventSeverity, EventCategory, EventType, EventSource, EventMetadata
from app.platform_contracts.redaction import SensitiveDataSanitizer


class EventSchema(BaseModel):
    schema_id: str
    event_type: str
    required_fields: List[str] = Field(default_factory=list)


class NormalizedEvent(BaseModel):
    normalized_id: str = Field(default_factory=lambda: f"norm_{uuid.uuid4().hex[:12]}")
    event: EnterpriseEvent
    is_valid: bool = True
    normalized_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class EventNormalizationRule(BaseModel):
    rule_id: str
    name: str


class EventSchemaRegistry:
    def __init__(self) -> None:
        self._schemas: Dict[str, EventSchema] = {}


class EventNormalizer:
    """Deterministically normalizes raw domain events into standard EnterpriseEvent models."""

    def __init__(self) -> None:
        self.sanitizer = SensitiveDataSanitizer()

    def normalize(
        self,
        tenant_id: str,
        raw_event: Dict[str, Any],
        source_id: str = "src_raw",
        source_name: str = "RawSource",
    ) -> NormalizedEvent:
        event_type_str = str(raw_event.get("event_type", "CUSTOM_EVENT")).upper()
        try:
            evt_type = EventType(event_type_str)
        except ValueError:
            evt_type = EventType.CUSTOM_EVENT

        severity_str = str(raw_event.get("severity", "MEDIUM")).upper()
        try:
            sev = EventSeverity(severity_str)
        except ValueError:
            sev = EventSeverity.MEDIUM

        category_str = str(raw_event.get("category", "OPERATIONAL")).upper()
        try:
            cat = EventCategory(category_str)
        except ValueError:
            cat = EventCategory.OPERATIONAL

        raw_payload = raw_event.get("payload", raw_event)
        sanitized_payload = self.sanitizer.sanitize_copy(raw_payload)

        idemp_ref = raw_event.get("idempotency_key", raw_event.get("idempotency_reference"))

        evt = EnterpriseEvent(
            tenant_id=tenant_id,
            source=EventSource(source_id=source_id, source_name=source_name),
            event_type=evt_type,
            category=cat,
            severity=sev,
            metadata=EventMetadata(payload=sanitized_payload),
            idempotency_reference=idemp_ref,
        )
        return NormalizedEvent(event=evt, is_valid=True)
