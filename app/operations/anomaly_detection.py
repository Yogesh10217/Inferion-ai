"""
Anomaly Detection Module for Phase 5.68.
Detects statistical, rule-based, and probe-based anomalies in operational telemetry.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from app.deployment.secrets import SecretsSanitizer
from app.operations.observability_engine import ObservationResult


class AnomalyType(str, Enum):
    LATENCY_SPIKE = "LATENCY_SPIKE"
    ERROR_RATE_SPIKE = "ERROR_RATE_SPIKE"
    AVAILABILITY_DROP = "AVAILABILITY_DROP"
    HEALTH_REGRESSION = "HEALTH_REGRESSION"
    DEPENDENCY_FAILURE = "DEPENDENCY_FAILURE"
    DEPLOYMENT_REGRESSION = "DEPLOYMENT_REGRESSION"
    RESOURCE_SATURATION = "RESOURCE_SATURATION"
    REPEATED_RESTART = "REPEATED_RESTART"
    PROBE_FAILURE = "PROBE_FAILURE"


class AnomalySeverity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"
    EMERGENCY = "EMERGENCY"


@dataclass
class Anomaly:
    anomaly_type: AnomalyType
    severity: AnomalySeverity
    timestamp: str
    baseline: float
    observed_value: float
    threshold: float
    evidence: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "anomaly_type": self.anomaly_type.value,
            "severity": self.severity.value,
            "timestamp": self.timestamp,
            "baseline": self.baseline,
            "observed_value": self.observed_value,
            "threshold": self.threshold,
            "evidence": SecretsSanitizer.sanitize_structure(self.evidence),
        }


class RuleBasedAnomalyDetector:
    """Evaluates telemetry observations against operational baselines to detect anomalies."""

    def __init__(
        self,
        latency_p95_threshold: float = 500.0,
        error_rate_threshold: float = 0.01,
        availability_threshold: float = 0.999,
    ) -> None:
        self.latency_p95_threshold = latency_p95_threshold
        self.error_rate_threshold = error_rate_threshold
        self.availability_threshold = availability_threshold

    def detect_anomalies(self, observation: ObservationResult) -> List[Anomaly]:
        anomalies = []
        now_iso = datetime.now(timezone.utc).isoformat()
        app_m = observation.application_metrics
        health_m = observation.health_metrics
        dep_m = observation.dependency_metrics
        ev_level = observation.evidence_level

        # 1. Latency Spike
        p95 = float(app_m.get("latency_p95", 0.0))
        if p95 > self.latency_p95_threshold:
            sev = AnomalySeverity.EMERGENCY if p95 > 2000.0 else (AnomalySeverity.CRITICAL if p95 > 1000.0 else AnomalySeverity.WARNING)
            anomalies.append(
                Anomaly(
                    anomaly_type=AnomalyType.LATENCY_SPIKE,
                    severity=sev,
                    timestamp=now_iso,
                    baseline=100.0,
                    observed_value=p95,
                    threshold=self.latency_p95_threshold,
                    evidence={"evidence_level": ev_level, "metric": "latency_p95", "observed": p95},
                )
            )

        # 2. Error Rate Spike
        err_rate = float(app_m.get("error_rate", 0.0))
        if err_rate > self.error_rate_threshold:
            sev = AnomalySeverity.EMERGENCY if err_rate > 0.10 else (AnomalySeverity.CRITICAL if err_rate > 0.05 else AnomalySeverity.WARNING)
            anomalies.append(
                Anomaly(
                    anomaly_type=AnomalyType.ERROR_RATE_SPIKE,
                    severity=sev,
                    timestamp=now_iso,
                    baseline=0.001,
                    observed_value=err_rate,
                    threshold=self.error_rate_threshold,
                    evidence={"evidence_level": ev_level, "metric": "error_rate", "observed": err_rate},
                )
            )

        # 3. Availability Drop
        avail = float(app_m.get("availability", 1.0))
        if avail < self.availability_threshold:
            sev = AnomalySeverity.EMERGENCY if avail < 0.95 else AnomalySeverity.CRITICAL
            anomalies.append(
                Anomaly(
                    anomaly_type=AnomalyType.AVAILABILITY_DROP,
                    severity=sev,
                    timestamp=now_iso,
                    baseline=0.9999,
                    observed_value=avail,
                    threshold=self.availability_threshold,
                    evidence={"evidence_level": ev_level, "metric": "availability", "observed": avail},
                )
            )

        # 4. Probe Failure & Health Regression
        if not health_m.get("live", True) or not health_m.get("ready", True) or not health_m.get("health", True):
            anomalies.append(
                Anomaly(
                    anomaly_type=AnomalyType.PROBE_FAILURE,
                    severity=AnomalySeverity.CRITICAL,
                    timestamp=now_iso,
                    baseline=1.0,
                    observed_value=0.0,
                    threshold=1.0,
                    evidence={"evidence_level": ev_level, "probes": health_m},
                )
            )
            anomalies.append(
                Anomaly(
                    anomaly_type=AnomalyType.HEALTH_REGRESSION,
                    severity=AnomalySeverity.CRITICAL,
                    timestamp=now_iso,
                    baseline=1.0,
                    observed_value=0.0,
                    threshold=1.0,
                    evidence={"evidence_level": ev_level, "probes": health_m},
                )
            )

        # 5. Dependency Failure
        failed_deps = [
            k for k, v in dep_m.items()
            if isinstance(v, dict) and v.get("status") in ("UNHEALTHY", "FAILED", "DOWN")
        ]
        if failed_deps:
            anomalies.append(
                Anomaly(
                    anomaly_type=AnomalyType.DEPENDENCY_FAILURE,
                    severity=AnomalySeverity.CRITICAL,
                    timestamp=now_iso,
                    baseline=0.0,
                    observed_value=float(len(failed_deps)),
                    threshold=0.0,
                    evidence={"evidence_level": ev_level, "failed_dependencies": failed_deps},
                )
            )

        return anomalies
