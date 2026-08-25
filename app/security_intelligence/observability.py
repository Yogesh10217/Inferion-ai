"""Prometheus Security Observability Metrics Subsystem (Phase 5.32)."""

import logging
from typing import Dict, Any, Optional
from prometheus_client import Counter, Gauge

from app.platform_contracts.observability import MetricNameValidator, SafeMetricLabelSanitizer

logger = logging.getLogger(__name__)

SECURITY_SIGNALS_TOTAL = Counter("ai_security_signals_total", "Total security signals ingested", ["signal_type", "tenant_id"])
SECURITY_THREATS_TOTAL = Counter("ai_security_threats_total", "Total security threats detected", ["threat_type", "tenant_id"])
SECURITY_VULNERABILITIES_TOTAL = Counter("ai_security_vulnerabilities_total", "Total security vulnerabilities discovered", ["severity", "tenant_id"])
SECURITY_INCIDENTS_TOTAL = Counter("ai_security_incidents_total", "Total security incidents detected", ["severity", "tenant_id"])
SECURITY_POSTURE_SCORE = Gauge("ai_security_posture_score", "Current security posture score", ["tenant_id"])
SECURITY_TRUST_SCORE = Gauge("ai_security_trust_score", "Current security trust score", ["tenant_id"])


class SecurityMetricsCollector:
    """Collects security metrics following standard ai_security_* conventions with sanitized labels."""

    def record_signal(self, signal_type: str, tenant_id: str) -> None:
        labels = SafeMetricLabelSanitizer.sanitize_labels({"signal_type": signal_type, "tenant_id": tenant_id})
        SECURITY_SIGNALS_TOTAL.labels(signal_type=labels["signal_type"], tenant_id=labels["tenant_id"]).inc()

    def record_threat(self, threat_type: str, tenant_id: str) -> None:
        labels = SafeMetricLabelSanitizer.sanitize_labels({"threat_type": threat_type, "tenant_id": tenant_id})
        SECURITY_THREATS_TOTAL.labels(threat_type=labels["threat_type"], tenant_id=labels["tenant_id"]).inc()

    def record_vulnerability(self, severity: str, tenant_id: str) -> None:
        labels = SafeMetricLabelSanitizer.sanitize_labels({"severity": severity, "tenant_id": tenant_id})
        SECURITY_VULNERABILITIES_TOTAL.labels(severity=labels["severity"], tenant_id=labels["tenant_id"]).inc()

    def record_incident(self, severity: str, tenant_id: str) -> None:
        labels = SafeMetricLabelSanitizer.sanitize_labels({"severity": severity, "tenant_id": tenant_id})
        SECURITY_INCIDENTS_TOTAL.labels(severity=labels["severity"], tenant_id=labels["tenant_id"]).inc()

    def record_posture(self, score: float, tenant_id: str) -> None:
        labels = SafeMetricLabelSanitizer.sanitize_labels({"tenant_id": tenant_id})
        SECURITY_POSTURE_SCORE.labels(tenant_id=labels["tenant_id"]).set(score)

    def record_trust(self, score: float, tenant_id: str) -> None:
        labels = SafeMetricLabelSanitizer.sanitize_labels({"tenant_id": tenant_id})
        SECURITY_TRUST_SCORE.labels(tenant_id=labels["tenant_id"]).set(score)
