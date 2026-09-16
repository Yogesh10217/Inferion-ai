"""Cross-domain operational signal intelligence with SensitiveDataSanitizer enforcing metadata protection."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict

from pydantic import BaseModel, Field

from app.platform_contracts.redaction import SensitiveDataSanitizer


class OperationalSignalType(str, Enum):
    METRIC_SIGNAL = "METRIC_SIGNAL"
    LOG_SIGNAL = "LOG_SIGNAL"
    TRACE_SIGNAL = "TRACE_SIGNAL"
    MODEL_SIGNAL = "MODEL_SIGNAL"
    SECURITY_SIGNAL = "SECURITY_SIGNAL"
    INFRASTRUCTURE_SIGNAL = "INFRASTRUCTURE_SIGNAL"


class OperationalSignal(BaseModel):
    signal_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    service_id: str
    signal_type: OperationalSignalType
    source_domain: str
    payload: Dict[str, Any] = Field(default_factory=dict)
    sanitized: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class OperationalSignalEngine:
    """Ingests and sanitizes cross-domain operational signals ensuring zero credential leakage."""

    def __init__(self) -> None:
        self.sanitizer = SensitiveDataSanitizer()

    def ingest_signal(
        self,
        tenant_id: str,
        service_id: str,
        signal_type: OperationalSignalType,
        source_domain: str,
        raw_payload: Dict[str, Any],
    ) -> OperationalSignal:
        sanitized_payload = self.sanitizer.sanitize_metadata(raw_payload)

        return OperationalSignal(
            tenant_id=tenant_id,
            service_id=service_id,
            signal_type=signal_type,
            source_domain=source_domain,
            payload=sanitized_payload,
            sanitized=True,
        )
