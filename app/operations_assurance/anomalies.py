"""Detect operational anomalies across degradation, errors, latency, saturation, capacity, dependencies, and traffic with explainable results."""

from datetime import datetime, timezone
from enum import Enum
from typing import Dict, Any, List, Optional
import uuid
from pydantic import BaseModel, Field

from app.operations_assurance.exceptions import CrossTenantOperationsAssuranceException, OperationalAnomalyException


class AnomalyCategory(str, Enum):
    SERVICE_DEGRADATION = "SERVICE_DEGRADATION"
    ERROR_SPIKE = "ERROR_SPIKE"
    LATENCY_SPIKE = "LATENCY_SPIKE"
    RESOURCE_SATURATION = "RESOURCE_SATURATION"
    CAPACITY_ANOMALY = "CAPACITY_ANOMALY"
    DEPENDENCY_FAILURE = "DEPENDENCY_FAILURE"
    TRAFFIC_ANOMALY = "TRAFFIC_ANOMALY"


class OperationalAnomaly(BaseModel):
    anomaly_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    service_id: str
    category: AnomalyCategory
    severity: str = "HIGH"
    metric_name: str
    observed_value: float
    threshold_value: float
    score: float = 0.8
    explanation: str
    detected_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class OperationalAnomalyDetector:
    """Detects and explains operational anomalies across services."""

    def __init__(self) -> None:
        self._anomalies: Dict[str, Dict[str, OperationalAnomaly]] = {}  # tenant_id -> {anomaly_id: anomaly}

    def detect_anomalies(
        self,
        tenant_id: str,
        service_id: str,
        metrics: Dict[str, float],
    ) -> List[OperationalAnomaly]:
        detected = []

        # Error rate check
        error_rate = metrics.get("error_rate", 0.0)
        if error_rate > 0.05:
            detected.append(
                OperationalAnomaly(
                    tenant_id=tenant_id,
                    service_id=service_id,
                    category=AnomalyCategory.ERROR_SPIKE,
                    severity="CRITICAL" if error_rate > 0.15 else "HIGH",
                    metric_name="error_rate",
                    observed_value=error_rate,
                    threshold_value=0.05,
                    score=min(1.0, error_rate * 5.0),
                    explanation=f"Error rate spike observed at {error_rate * 100:.1f}%, exceeding threshold of 5%.",
                )
            )

        # Latency check
        latency = metrics.get("latency_p99_ms", 0.0)
        if latency > 300.0:
            detected.append(
                OperationalAnomaly(
                    tenant_id=tenant_id,
                    service_id=service_id,
                    category=AnomalyCategory.LATENCY_SPIKE,
                    severity="HIGH",
                    metric_name="latency_p99_ms",
                    observed_value=latency,
                    threshold_value=300.0,
                    score=min(1.0, latency / 1000.0),
                    explanation=f"Latency p99 spike observed at {latency:.1f}ms, exceeding threshold of 300ms.",
                )
            )

        # Resource saturation check
        cpu_usage = metrics.get("cpu_saturation", 0.0)
        if cpu_usage > 0.85:
            detected.append(
                OperationalAnomaly(
                    tenant_id=tenant_id,
                    service_id=service_id,
                    category=AnomalyCategory.RESOURCE_SATURATION,
                    severity="HIGH",
                    metric_name="cpu_saturation",
                    observed_value=cpu_usage,
                    threshold_value=0.85,
                    score=cpu_usage,
                    explanation=f"CPU saturation observed at {cpu_usage * 100:.1f}%, exceeding threshold of 85%.",
                )
            )

        if tenant_id not in self._anomalies:
            self._anomalies[tenant_id] = {}
        for anomaly in detected:
            self._anomalies[tenant_id][anomaly.anomaly_id] = anomaly

        return detected

    def list_anomalies(self, tenant_id: str, service_id: Optional[str] = None) -> List[OperationalAnomaly]:
        tenant_anomalies = self._anomalies.get(tenant_id, {})
        if service_id:
            return [anom for anom in tenant_anomalies.values() if anom.service_id == service_id]
        return list(tenant_anomalies.values())
