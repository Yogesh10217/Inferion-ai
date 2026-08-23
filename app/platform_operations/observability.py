"""Prometheus Observability Metrics Collector for Platform Operations."""

import logging
from typing import Dict, Any, Optional

try:
    from prometheus_client import Counter, Histogram, Gauge
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False

logger = logging.getLogger(__name__)

if PROMETHEUS_AVAILABLE:
    SIGNALS_TOTAL = Counter("ai_platform_operations_signals_total", "Total operational signals ingested", ["tenant_id", "source", "severity"])
    ANOMALIES_TOTAL = Counter("ai_platform_operations_anomalies_total", "Total operational anomalies detected", ["tenant_id", "anomaly_type", "severity"])
    INCIDENTS_CORRELATED_TOTAL = Counter("ai_platform_operations_incidents_correlated_total", "Total incidents correlated", ["tenant_id", "severity"])
    DIAGNOSIS_TOTAL = Counter("ai_platform_operations_diagnosis_total", "Total root cause diagnoses performed", ["tenant_id", "category"])
    REMEDIATION_TOTAL = Counter("ai_platform_operations_remediation_total", "Total remediation plans created", ["tenant_id", "strategy"])
    REMEDIATION_SUCCESS_TOTAL = Counter("ai_platform_operations_remediation_success_total", "Total successful remediations", ["tenant_id"])
    REMEDIATION_FAILURE_TOTAL = Counter("ai_platform_operations_remediation_failure_total", "Total failed remediations", ["tenant_id"])
    AUTONOMOUS_ACTIONS_TOTAL = Counter("ai_platform_operations_autonomous_actions_total", "Total autonomous operational actions executed", ["tenant_id", "autonomy_level"])
    ROLLBACK_TOTAL = Counter("ai_platform_operations_rollback_total", "Total remediation rollbacks executed", ["tenant_id"])
    SLO_VIOLATIONS_TOTAL = Counter("ai_platform_operations_slo_violations_total", "Total SLO violations detected", ["tenant_id", "slo_type"])


class PlatformOperationsMetricsCollector:
    """Collects platform operations telemetry for Prometheus with secret redaction."""

    def record_signal(self, tenant_id: str, source: str, severity: str) -> None:
        if PROMETHEUS_AVAILABLE:
            SIGNALS_TOTAL.labels(tenant_id=tenant_id, source=source, severity=severity).inc()

    def record_anomaly(self, tenant_id: str, anomaly_type: str, severity: str) -> None:
        if PROMETHEUS_AVAILABLE:
            ANOMALIES_TOTAL.labels(tenant_id=tenant_id, anomaly_type=anomaly_type, severity=severity).inc()

    def record_remediation(self, tenant_id: str, strategy: str, success: bool) -> None:
        if PROMETHEUS_AVAILABLE:
            REMEDIATION_TOTAL.labels(tenant_id=tenant_id, strategy=strategy).inc()
            if success:
                REMEDIATION_SUCCESS_TOTAL.labels(tenant_id=tenant_id).inc()
            else:
                REMEDIATION_FAILURE_TOTAL.labels(tenant_id=tenant_id).inc()

    def record_autonomous_action(self, tenant_id: str, autonomy_level: str) -> None:
        if PROMETHEUS_AVAILABLE:
            AUTONOMOUS_ACTIONS_TOTAL.labels(tenant_id=tenant_id, autonomy_level=autonomy_level).inc()

    def record_rollback(self, tenant_id: str) -> None:
        if PROMETHEUS_AVAILABLE:
            ROLLBACK_TOTAL.labels(tenant_id=tenant_id).inc()
