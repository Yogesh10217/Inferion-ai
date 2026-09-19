"""Security Assurance Observability & Prometheus Metrics Engine."""

import logging

try:
    from prometheus_client import Counter, Gauge

    # Prometheus metrics prefixed with ai_security_assurance_*
    SECURITY_ASSURANCE_ASSETS_GAUGE = Gauge(
        "ai_security_assurance_monitored_assets_total", "Total monitored security assets per tenant", ["tenant_id"]
    )
    SECURITY_ASSURANCE_POSTURE_GAUGE = Gauge(
        "ai_security_assurance_posture_score", "Current security posture score per tenant", ["tenant_id"]
    )
    SECURITY_ASSURANCE_THREATS_COUNTER = Counter(
        "ai_security_assurance_threats_detected_total", "Total security threats detected", ["tenant_id", "severity"]
    )
    SECURITY_ASSURANCE_INCIDENTS_COUNTER = Counter(
        "ai_security_assurance_incidents_created_total", "Total security incidents created", ["tenant_id", "severity"]
    )
    PROMETHEUS_AVAILABLE = True
except Exception:
    PROMETHEUS_AVAILABLE = False

logger = logging.getLogger(__name__)


class SecurityObservabilityEngine:
    """Manages telemetry, logging, and Prometheus metrics for security assurance platform."""

    def record_asset_count(self, tenant_id: str, count: int) -> None:
        if PROMETHEUS_AVAILABLE:
            try:
                SECURITY_ASSURANCE_ASSETS_GAUGE.labels(tenant_id=tenant_id).set(count)
            except Exception as e:
                logger.debug(f"Failed to record Prometheus metric: {e}")

    def record_posture_score(self, tenant_id: str, score: float) -> None:
        if PROMETHEUS_AVAILABLE:
            try:
                SECURITY_ASSURANCE_POSTURE_GAUGE.labels(tenant_id=tenant_id).set(score)
            except Exception as e:
                logger.debug(f"Failed to record Prometheus metric: {e}")

    def record_threat_detected(self, tenant_id: str, severity: str) -> None:
        if PROMETHEUS_AVAILABLE:
            try:
                SECURITY_ASSURANCE_THREATS_COUNTER.labels(tenant_id=tenant_id, severity=severity).inc()
            except Exception as e:
                logger.debug(f"Failed to record Prometheus metric: {e}")

    def record_incident_created(self, tenant_id: str, severity: str) -> None:
        if PROMETHEUS_AVAILABLE:
            try:
                SECURITY_ASSURANCE_INCIDENTS_COUNTER.labels(tenant_id=tenant_id, severity=severity).inc()
            except Exception as e:
                logger.debug(f"Failed to record Prometheus metric: {e}")
