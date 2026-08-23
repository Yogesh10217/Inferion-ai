"""Deterministic Operational Anomaly Detection Engine."""

from datetime import datetime, timezone
from enum import Enum
import uuid
import logging
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field

from app.platform_operations.signals import OperationalSignal, SignalSeverity, SignalType

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class AnomalyType(str, Enum):
    THRESHOLD_BREACH = "THRESHOLD_BREACH"
    RATE_CHANGE = "RATE_CHANGE"
    BASELINE_DEVIATION = "BASELINE_DEVIATION"
    ERROR_SPIKE = "ERROR_SPIKE"
    LATENCY_SPIKE = "LATENCY_SPIKE"
    COST_SPIKE = "COST_SPIKE"
    SAFETY_REGRESSION = "SAFETY_REGRESSION"
    DEPLOYMENT_REGRESSION = "DEPLOYMENT_REGRESSION"


class AnomalySeverity(str, Enum):
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class Anomaly(BaseModel):
    anomaly_id: str = Field(default_factory=lambda: f"anom_{uuid.uuid4().hex[:10]}")
    tenant_id: str = "global"
    service_id: Optional[str] = None
    resource_id: Optional[str] = None
    anomaly_type: AnomalyType
    severity: AnomalySeverity = AnomalySeverity.MEDIUM
    title: str
    description: str = ""
    evidence: List[str] = Field(default_factory=list)
    triggering_signal_ids: List[str] = Field(default_factory=list)
    detected_at: datetime = Field(default_factory=_now)


class AnomalyDetector:
    """Detects deterministic operational anomalies based on explicit rules and metric thresholds."""

    def __init__(self) -> None:
        self._anomalies: Dict[str, Anomaly] = {}

    def detect_anomalies(
        self,
        tenant_id: str,
        signals: List[OperationalSignal],
        latency_p95_threshold_ms: float = 2000.0,
        error_rate_threshold_pct: float = 5.0,
    ) -> List[Anomaly]:
        new_anomalies: List[Anomaly] = []

        # 1. Inspect signals for error spikes or latency spikes
        error_signals = [s for s in signals if s.severity in (SignalSeverity.ERROR, SignalSeverity.CRITICAL)]
        if len(error_signals) >= 3:
            service_id = error_signals[0].service_id
            anom = Anomaly(
                tenant_id=tenant_id,
                service_id=service_id,
                anomaly_type=AnomalyType.ERROR_SPIKE,
                severity=AnomalySeverity.HIGH,
                title=f"Error Spike Detected in Service {service_id or 'unknown'}",
                description=f"Received {len(error_signals)} error/critical signals within time window.",
                evidence=[f"Signal {s.signal_id}: {s.message}" for s in error_signals[:5]],
                triggering_signal_ids=[s.signal_id for s in error_signals],
            )
            self._anomalies[anom.anomaly_id] = anom
            new_anomalies.append(anom)

        # 2. Inspect signals for latency spikes
        for sig in signals:
            if "latency_ms" in sig.metrics and sig.metrics["latency_ms"] > latency_p95_threshold_ms:
                anom = Anomaly(
                    tenant_id=tenant_id,
                    service_id=sig.service_id,
                    anomaly_type=AnomalyType.LATENCY_SPIKE,
                    severity=AnomalySeverity.MEDIUM,
                    title=f"Latency Spike Detected ({sig.metrics['latency_ms']:.1f} ms)",
                    description=f"Latency for service {sig.service_id} exceeded threshold of {latency_p95_threshold_ms} ms.",
                    evidence=[f"Signal {sig.signal_id} reported latency_ms={sig.metrics['latency_ms']:.1f}"],
                    triggering_signal_ids=[sig.signal_id],
                )
                self._anomalies[anom.anomaly_id] = anom
                new_anomalies.append(anom)

        # 3. Inspect deployment regressions
        dep_signals = [s for s in signals if s.signal_type == SignalType.DEPLOYMENT_EVENT]
        if dep_signals and error_signals:
            anom = Anomaly(
                tenant_id=tenant_id,
                service_id=dep_signals[0].service_id,
                anomaly_type=AnomalyType.DEPLOYMENT_REGRESSION,
                severity=AnomalySeverity.HIGH,
                title="Deployment Regression Detected",
                description="Errors surged immediately following recent deployment event.",
                evidence=[
                    f"Deployment event signal {dep_signals[0].signal_id}: {dep_signals[0].message}",
                    f"Followed by {len(error_signals)} error signals.",
                ],
                triggering_signal_ids=[dep_signals[0].signal_id] + [s.signal_id for s in error_signals],
            )
            self._anomalies[anom.anomaly_id] = anom
            new_anomalies.append(anom)

        logger.info(f"[ANOMALY DETECTOR] Detected {len(new_anomalies)} anomalies for tenant '{tenant_id}'")
        return new_anomalies

    def list_anomalies(self, tenant_id: str) -> List[Anomaly]:
        return [a for a in self._anomalies.values() if a.tenant_id in (tenant_id, "global")]
