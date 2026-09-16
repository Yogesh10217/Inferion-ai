"""Runtime anomaly detector for Runtime Intelligence (Phase 5.57)."""

import logging
from typing import Any, Dict, List, Optional

from app.runtime_intelligence.baseline import BaselineManager
from app.runtime_intelligence.models import RuntimeAnomaly, RuntimeAnomalySeverity

logger = logging.getLogger(__name__)


class RuntimeAnomalyDetector:
    """Detects explainable runtime anomalies across system dimensions using thresholds and historical baselines."""

    def __init__(self, baseline_manager: Optional[BaselineManager] = None) -> None:
        self.baseline_manager = baseline_manager or BaselineManager()

    def detect_anomalies(
        self, tenant_id: str, metrics: Dict[str, Any], subsystem: str = "global"
    ) -> List[RuntimeAnomaly]:
        anomalies: List[RuntimeAnomaly] = []

        # 1. Latency Check against baseline
        latency = float(metrics.get("latency_p99_ms", metrics.get("latency_p99", 120.0)))
        bl_latency = self.baseline_manager.get_or_create_baseline(tenant_id, f"{subsystem}_latency", default_mean=150.0, default_std=30.0)
        if latency > bl_latency.confidence_band_upper:
            severity = RuntimeAnomalySeverity.CRITICAL if latency > (bl_latency.expected_mean * 2.5) else (
                RuntimeAnomalySeverity.HIGH if latency > (bl_latency.expected_mean * 1.8) else RuntimeAnomalySeverity.MEDIUM
            )
            anomalies.append(
                RuntimeAnomaly(
                    tenant_id=tenant_id,
                    anomaly_type="LATENCY_BASELINE_VIOLATION",
                    severity=severity,
                    description=f"P99 Latency of {latency:.1f}ms exceeds baseline upper band of {bl_latency.confidence_band_upper:.1f}ms",
                    metric_name="latency_p99_ms",
                    observed_value=latency,
                    expected_value=bl_latency.expected_mean,
                    confidence=0.92,
                )
            )

        # 2. Error Rate Check against baseline
        error_rate = float(metrics.get("error_rate", 0.001))
        bl_error = self.baseline_manager.get_or_create_baseline(tenant_id, f"{subsystem}_error_rate", default_mean=0.01, default_std=0.005)
        if error_rate > bl_error.confidence_band_upper:
            severity = RuntimeAnomalySeverity.CRITICAL if error_rate > 0.10 else (
                RuntimeAnomalySeverity.HIGH if error_rate > 0.05 else RuntimeAnomalySeverity.MEDIUM
            )
            anomalies.append(
                RuntimeAnomaly(
                    tenant_id=tenant_id,
                    anomaly_type="ERROR_RATE_SPIKE",
                    severity=severity,
                    description=f"Error rate of {error_rate * 100:.1f}% exceeds baseline upper threshold of {bl_error.confidence_band_upper * 100:.1f}%",
                    metric_name="error_rate",
                    observed_value=error_rate,
                    expected_value=bl_error.expected_mean,
                    confidence=0.95,
                )
            )

        # 3. CPU/Memory Saturation Check
        cpu_usage = float(metrics.get("cpu_utilization", metrics.get("cpu_usage", 0.0)))
        if cpu_usage > 0.90:
            anomalies.append(
                RuntimeAnomaly(
                    tenant_id=tenant_id,
                    anomaly_type="RESOURCE_SATURATION_CPU",
                    severity=RuntimeAnomalySeverity.HIGH if cpu_usage < 0.95 else RuntimeAnomalySeverity.CRITICAL,
                    description=f"CPU utilization at {cpu_usage * 100:.1f}% exceeds safe operational ceiling of 90%",
                    metric_name="cpu_utilization",
                    observed_value=cpu_usage,
                    expected_value=0.70,
                    confidence=0.90,
                )
            )

        logger.info(f"Detected {len(anomalies)} runtime anomalies for tenant '{tenant_id}' (subsystem: '{subsystem}')")
        return anomalies

    def detect_time_series_anomalies(
        self, tenant_id: str, subsystem: str, time_series_data: List[Dict[str, Any]]
    ) -> List[RuntimeAnomaly]:
        """Detects anomalies across time-series data points."""
        if not time_series_data:
            return []

        values = [float(p.get("value", 0.0)) for p in time_series_data if "value" in p]
        if not values:
            return []

        mean_val = sum(values) / len(values)
        variance = sum((v - mean_val) ** 2 for v in values) / len(values)
        std_dev = variance ** 0.5

        anomalies: List[RuntimeAnomaly] = []
        for point in time_series_data:
            val = float(point.get("value", 0.0))
            if std_dev > 0 and abs(val - mean_val) > (2.5 * std_dev):
                anomalies.append(
                    RuntimeAnomaly(
                        tenant_id=tenant_id,
                        anomaly_type="TIME_SERIES_OUTLIER_SPIKE",
                        severity=RuntimeAnomalySeverity.HIGH,
                        description=f"Time-series value {val:.2f} deviates significantly from window mean {mean_val:.2f} (std={std_dev:.2f})",
                        metric_name=point.get("metric_name", "time_series_metric"),
                        observed_value=val,
                        expected_value=round(mean_val, 2),
                        confidence=0.94,
                    )
                )
        return anomalies
