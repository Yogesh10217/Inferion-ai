"""Anomaly Detection Engine (Phase 5.31)."""

from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.reliability_platform.signals import ReliabilitySignal, SignalSeverity


class AnomalyType(str, Enum):
    LATENCY_SPIKE = "LATENCY_SPIKE"
    ERROR_RATE_BURST = "ERROR_RATE_BURST"
    SATURATION_BREACH = "SATURATION_BREACH"
    MEMORY_LEAK = "MEMORY_LEAK"
    MODEL_DRIFT = "MODEL_DRIFT"


class AnomalySeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class Anomaly(BaseModel):
    anomaly_id: str = Field(default_factory=lambda: f"anom_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    service_id: str
    anomaly_type: AnomalyType
    severity: AnomalySeverity
    confidence_score: float = 0.95
    signal_ids: List[str] = Field(default_factory=list)
    detected_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AnomalyDetector:
    """Detects operational anomalies from processed signals."""

    def detect_anomaly(self, signals: List[ReliabilitySignal]) -> Optional[Anomaly]:
        if not signals:
            return None
        first_sig = signals[0]

        high_severity_count = sum(1 for s in signals if s.severity in (SignalSeverity.ERROR, SignalSeverity.CRITICAL))
        if high_severity_count >= 1:
            return Anomaly(
                tenant_id=first_sig.tenant_id,
                service_id=first_sig.service_id,
                anomaly_type=AnomalyType.ERROR_RATE_BURST,
                severity=AnomalySeverity.HIGH,
                signal_ids=[s.signal_id for s in signals],
            )
        return None
