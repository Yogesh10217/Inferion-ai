"""Prometheus Observability Metrics Subsystem (Phase 5.31)."""

import logging

from prometheus_client import Counter

from app.platform_contracts.observability import SafeMetricLabelSanitizer

logger = logging.getLogger(__name__)

# Metrics
RELIABILITY_INCIDENTS_TOTAL = Counter(
    "ai_reliability_incident_total",
    "Total count of reliability incidents detected",
    ["severity", "tenant_id"],
)

RELIABILITY_SLO_BREACHES_TOTAL = Counter(
    "ai_reliability_slo_breaches_total",
    "Total count of SLO budget breaches",
    ["tenant_id"],
)

RELIABILITY_REMEDIATION_TOTAL = Counter(
    "ai_reliability_remediation_total",
    "Total count of delegated remediation actions",
    ["status", "tenant_id"],
)


class ReliabilityMetricsCollector:
    """Collects operational metrics following standard ai_reliability_* conventions."""

    def record_incident(self, severity: str, tenant_id: str) -> None:
        safe_labels = SafeMetricLabelSanitizer.sanitize_labels({"severity": severity, "tenant_id": tenant_id})
        RELIABILITY_INCIDENTS_TOTAL.labels(severity=safe_labels["severity"], tenant_id=safe_labels["tenant_id"]).inc()

    def record_slo_breach(self, tenant_id: str) -> None:
        safe_labels = SafeMetricLabelSanitizer.sanitize_labels({"tenant_id": tenant_id})
        RELIABILITY_SLO_BREACHES_TOTAL.labels(tenant_id=safe_labels["tenant_id"]).inc()

    def record_remediation(self, status: str, tenant_id: str) -> None:
        safe_labels = SafeMetricLabelSanitizer.sanitize_labels({"status": status, "tenant_id": tenant_id})
        RELIABILITY_REMEDIATION_TOTAL.labels(status=safe_labels["status"], tenant_id=safe_labels["tenant_id"]).inc()
