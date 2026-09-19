"""Cross-platform decision signals ingested from all 10 platform domains."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.platform_contracts.redaction import SensitiveDataSanitizer


class DecisionSignalType(str, Enum):
    CONTROL_VIOLATION = "CONTROL_VIOLATION"
    ANOMALY = "ANOMALY"
    DRIFT = "DRIFT"
    COST_SPIKE = "COST_SPIKE"
    CAPACITY_EXHAUSTION = "CAPACITY_EXHAUSTION"
    THREAT_DETECTED = "THREAT_DETECTED"
    SLOWDOWN = "SLOWDOWN"
    POLICY_BREACH = "POLICY_BREACH"


class DecisionSignalSource(str, Enum):
    CONTROL_ASSURANCE = "CONTROL_ASSURANCE"
    ACCESS_INTELLIGENCE = "ACCESS_INTELLIGENCE"
    INTEGRATION_INTELLIGENCE = "INTEGRATION_INTELLIGENCE"
    OPERATIONS_INTELLIGENCE = "OPERATIONS_INTELLIGENCE"
    FINOPS_INTELLIGENCE = "FINOPS_INTELLIGENCE"
    DATA_INTELLIGENCE = "DATA_INTELLIGENCE"
    MODEL_INTELLIGENCE = "MODEL_INTELLIGENCE"
    SECURITY_INTELLIGENCE = "SECURITY_INTELLIGENCE"
    EVENT_INTELLIGENCE = "EVENT_INTELLIGENCE"
    KNOWLEDGE_INTELLIGENCE = "KNOWLEDGE_INTELLIGENCE"


class DecisionSignalSeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class DecisionSignal(BaseModel):
    signal_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    source_domain: DecisionSignalSource
    signal_type: DecisionSignalType
    severity: DecisionSignalSeverity = DecisionSignalSeverity.MEDIUM
    title: str
    description: str = ""
    resource_id: Optional[str] = None
    resource_type: Optional[str] = None
    sanitized_payload: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DecisionSignalManager:
    """Ingests and sanitizes cross-platform telemetry signals for decision reasoning."""

    def __init__(self) -> None:
        self._signals: Dict[str, DecisionSignal] = {}

    def ingest_signal(
        self,
        tenant_id: str,
        source_domain: DecisionSignalSource,
        signal_type: DecisionSignalType,
        title: str,
        payload: Dict[str, Any],
        description: str = "",
        severity: DecisionSignalSeverity = DecisionSignalSeverity.MEDIUM,
        resource_id: Optional[str] = None,
        resource_type: Optional[str] = None,
    ) -> DecisionSignal:
        sanitized = SensitiveDataSanitizer.sanitize_metadata(payload)
        sig = DecisionSignal(
            tenant_id=tenant_id,
            source_domain=source_domain,
            signal_type=signal_type,
            severity=severity,
            title=title,
            description=description,
            resource_id=resource_id,
            resource_type=resource_type,
            sanitized_payload=sanitized,
        )
        self._signals[sig.signal_id] = sig
        return sig

    def list_signals(
        self, tenant_id: str, source_domain: Optional[DecisionSignalSource] = None
    ) -> List[DecisionSignal]:
        sigs = [s for s in self._signals.values() if s.tenant_id == tenant_id]
        if source_domain:
            sigs = [s for s in sigs if s.source_domain == source_domain]
        return sorted(sigs, key=lambda x: x.created_at, reverse=True)
