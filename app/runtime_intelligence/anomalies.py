"""Runtime anomaly detector for Runtime Intelligence (Phase 5.54)."""

import logging
from typing import List, Dict, Any
from app.runtime_intelligence.models import RuntimeAnomaly, RuntimeAnomalySeverity

logger = logging.getLogger(__name__)


class RuntimeAnomalyDetector:
    """Detects explainable runtime anomalies across system dimensions."""

    def detect_anomalies(
        self, tenant_id: str, metrics: Dict[str, Any]
    ) -> List[RuntimeAnomaly]:
        anomalies: List[RuntimeAnomaly] = []

        latency = metrics.get("latency_p99_ms", 120.0)
        if latency > 500.0:
            anomalies.append(
                RuntimeAnomaly(
                    tenant_id=tenant_id,
                    anomaly_type="UNEXPECTED_LATENCY_SPIKE",
                    severity=RuntimeAnomalySeverity.HIGH if latency > 1000.0 else RuntimeAnomalySeverity.MEDIUM,
                    description=f"P99 Latency of {latency:.1f}ms exceeds baseline of 150.0ms",
                    metric_name="latency_p99_ms",
                    observed_value=latency,
                    expected_value=150.0,
                )
            )

        error_rate = metrics.get("error_rate", 0.001)
        if error_rate > 0.05:
            anomalies.append(
                RuntimeAnomaly(
                    tenant_id=tenant_id,
                    anomaly_type="ERROR_RATE_SPIKE",
                    severity=RuntimeAnomalySeverity.CRITICAL if error_rate > 0.15 else RuntimeAnomalySeverity.HIGH,
                    description=f"Error rate of {error_rate * 100:.1f}% exceeds baseline threshold of 1.0%",
                    metric_name="error_rate",
                    observed_value=error_rate,
                    expected_value=0.01,
                )
            )

        logger.info(f"Detected {len(anomalies)} runtime anomalies for tenant '{tenant_id}'")
        return anomalies
