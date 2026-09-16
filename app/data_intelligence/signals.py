"""Data signal intelligence (Phase 5.43)."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.platform_contracts.redaction import SensitiveDataSanitizer


class DataSignalType(str, Enum):
    QUALITY_DEGRADED = "QUALITY_DEGRADED"
    FRESHNESS_LAG = "FRESHNESS_LAG"
    ANOMALY_DETECTED = "ANOMALY_DETECTED"
    DRIFT_DETECTED = "DRIFT_DETECTED"
    SCHEMA_CHANGED = "SCHEMA_CHANGED"
    PIPELINE_FAILED = "PIPELINE_FAILED"


class DataSignalSource(str, Enum):
    DATA_GOVERNANCE = "DATA_GOVERNANCE"
    EVENT_INTELLIGENCE = "EVENT_INTELLIGENCE"
    OPERATIONS_INTELLIGENCE = "OPERATIONS_INTELLIGENCE"
    AI_LIFECYCLE = "AI_LIFECYCLE"
    RELIABILITY_PLATFORM = "RELIABILITY_PLATFORM"
    CONTROL_ASSURANCE = "CONTROL_ASSURANCE"


class DataSignal(BaseModel):
    signal_id: str
    tenant_id: str
    dataset_id: str
    signal_type: DataSignalType
    source: DataSignalSource
    sanitized_payload: Dict[str, Any] = Field(default_factory=dict)
    emitted_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DataSignalManager:
    """Collects and processes sanitized data signals from cross-platform domain managers."""

    def __init__(self) -> None:
        self._signals: Dict[str, DataSignal] = {}
        self._sanitizer = SensitiveDataSanitizer()

    def emit_signal(
        self,
        tenant_id: str,
        dataset_id: str,
        signal_type: DataSignalType,
        source: DataSignalSource,
        payload: Optional[Dict[str, Any]] = None,
        signal_id: Optional[str] = None,
    ) -> DataSignal:
        sig_id = signal_id or f"sig-{uuid.uuid4().hex[:8]}"

        sanitized_pld = self._sanitizer.sanitize(payload or {})
        clean_pld = sanitized_pld if isinstance(sanitized_pld, dict) else {}

        sig = DataSignal(
            signal_id=sig_id,
            tenant_id=tenant_id,
            dataset_id=dataset_id,
            signal_type=signal_type,
            source=source,
            sanitized_payload=clean_pld,
        )
        self._signals[sig_id] = sig
        return sig

    def list_signals(self, tenant_id: str, dataset_id: Optional[str] = None) -> List[DataSignal]:
        sigs = [s for s in self._signals.values() if s.tenant_id == tenant_id]
        if dataset_id:
            sigs = [s for s in sigs if s.dataset_id == dataset_id]
        return sigs
