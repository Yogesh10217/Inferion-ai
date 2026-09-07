"""Sanitized Cross-Domain Unified Intelligence Signals for Phase 5.51 Enterprise AI Unified Intelligence."""

import logging
from enum import Enum
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.unified_intelligence.domains import IntelligenceDomain
from app.unified_intelligence.normalization_contracts import NormalizedSignal
from app.platform_contracts.redaction import SensitiveDataSanitizer

logger = logging.getLogger(__name__)


class UnifiedSignalSeverity(str, Enum):
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class UnifiedSignalType(str, Enum):
    SECURITY_FINDING = "SECURITY_FINDING"
    IDENTITY_ANOMALY = "IDENTITY_ANOMALY"
    OPERATIONAL_INCIDENT = "OPERATIONAL_INCIDENT"
    POLICY_VIOLATION = "POLICY_VIOLATION"
    KNOWLEDGE_CONFLICT = "KNOWLEDGE_CONFLICT"
    DATA_DRIFT = "DATA_DRIFT"
    MODEL_HALLUCINATION = "MODEL_HALLUCINATION"
    ACCESS_RISK = "ACCESS_RISK"
    CONTROL_FAILURE = "CONTROL_FAILURE"
    FINANCIAL_ANOMALY = "FINANCIAL_ANOMALY"


class UnifiedSignal(BaseModel):
    signal_id: str = Field(default_factory=lambda: f"unif-sig-{uuid.uuid4().hex[:8]}")
    correlation_id: str = Field(default_factory=lambda: f"corr-{uuid.uuid4().hex[:8]}")
    tenant_id: str
    domain: IntelligenceDomain
    source_reference: str
    signal_type: str
    severity: str
    sanitized_payload: Dict[str, Any] = Field(default_factory=dict)
    confidence_score: float = 0.9
    risk_score: float = 0.5
    trust_score: float = 85.0
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @classmethod
    def from_normalized_signal(cls, normalized: NormalizedSignal) -> "UnifiedSignal":
        return cls(
            signal_id=normalized.signal_id,
            correlation_id=normalized.correlation_id,
            tenant_id=normalized.tenant_id,
            domain=normalized.domain,
            source_reference=normalized.entity_reference,
            signal_type=normalized.signal_type,
            severity=normalized.severity,
            sanitized_payload=normalized.sanitized_payload,
            confidence_score=normalized.confidence_score,
            risk_score=normalized.risk_score
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "signal_id": self.signal_id,
            "correlation_id": self.correlation_id,
            "tenant_id": self.tenant_id,
            "domain": self.domain.value if hasattr(self.domain, 'value') else str(self.domain),
            "entity_reference": self.source_reference,
            "source_reference": self.source_reference,
            "signal_type": self.signal_type,
            "severity": self.severity,
            "confidence_score": round(self.confidence_score, 4),
            "risk_score": round(self.risk_score, 4),
            "sanitized_payload": self.sanitized_payload,
            "created_at": self.timestamp.isoformat()
        }


class UnifiedSignalStore:
    """In-memory store for sanitized unified signals with strict secret redaction."""

    def __init__(self) -> None:
        self._signals: Dict[str, UnifiedSignal] = {}
        self.sanitizer = SensitiveDataSanitizer()

    def ingest_signal(
        self,
        tenant_id: str,
        domain: IntelligenceDomain,
        source_reference: str,
        signal_type: str,
        severity: str,
        raw_payload: Dict[str, Any],
        confidence_score: float = 0.9,
        trust_score: float = 85.0,
        correlation_id: Optional[str] = None,
    ) -> UnifiedSignal:
        sanitized_payload = self.sanitizer.sanitize_copy(raw_payload)

        signal = UnifiedSignal(
            correlation_id=correlation_id or f"corr-{uuid.uuid4().hex[:8]}",
            tenant_id=tenant_id,
            domain=domain,
            source_reference=source_reference,
            signal_type=signal_type,
            severity=severity,
            sanitized_payload=sanitized_payload,
            confidence_score=confidence_score,
            trust_score=trust_score,
        )
        self._signals[signal.signal_id] = signal
        return signal

    def list_signals(self, tenant_id: str, domain: Optional[IntelligenceDomain] = None) -> List[UnifiedSignal]:
        results = [s for s in self._signals.values() if s.tenant_id == tenant_id]
        if domain:
            results = [s for s in results if s.domain == domain]
        return results
