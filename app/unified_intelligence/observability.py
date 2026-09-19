"""
Prometheus Observability Engine for Phase 5.51 Enterprise AI Unified Intelligence.

Defines and manages telemetry and metrics prefixed with ai_unified_intelligence_*.
"""

import logging

try:
    from prometheus_client import Counter, Gauge

    # Prometheus metrics prefixed with ai_unified_intelligence_*
    UNIFIED_INTELLIGENCE_SIGNALS_COUNTER = Counter(
        "ai_unified_intelligence_signals_processed_total",
        "Total unified domain signals processed",
        ["tenant_id", "domain"],
    )
    UNIFIED_INTELLIGENCE_SITUATIONS_COUNTER = Counter(
        "ai_unified_intelligence_situations_detected_total",
        "Total enterprise situations detected",
        ["tenant_id", "severity"],
    )
    UNIFIED_INTELLIGENCE_RISK_SCORE_GAUGE = Gauge(
        "ai_unified_intelligence_risk_score", "Overall cross-domain risk score per tenant", ["tenant_id"]
    )
    UNIFIED_INTELLIGENCE_ASSURANCE_SCORE_GAUGE = Gauge(
        "ai_unified_intelligence_assurance_score",
        "Overall cross-domain assurance posture score per tenant",
        ["tenant_id"],
    )
    PROMETHEUS_AVAILABLE = True
except Exception:
    PROMETHEUS_AVAILABLE = False

logger = logging.getLogger(__name__)


class UnifiedObservabilityEngine:
    """
    Manages telemetry, logging, and Prometheus metrics for the Unified Intelligence platform.
    """

    def record_signal_processed(self, tenant_id: str, domain: str) -> None:
        if PROMETHEUS_AVAILABLE:
            try:
                UNIFIED_INTELLIGENCE_SIGNALS_COUNTER.labels(tenant_id=tenant_id, domain=domain).inc()
            except Exception as e:
                logger.debug(f"Failed to record Prometheus metric: {e}")

    def record_situation_detected(self, tenant_id: str, severity: str) -> None:
        if PROMETHEUS_AVAILABLE:
            try:
                UNIFIED_INTELLIGENCE_SITUATIONS_COUNTER.labels(tenant_id=tenant_id, severity=severity).inc()
            except Exception as e:
                logger.debug(f"Failed to record Prometheus metric: {e}")

    def record_risk_score(self, tenant_id: str, score: float) -> None:
        if PROMETHEUS_AVAILABLE:
            try:
                UNIFIED_INTELLIGENCE_RISK_SCORE_GAUGE.labels(tenant_id=tenant_id).set(score)
            except Exception as e:
                logger.debug(f"Failed to record Prometheus metric: {e}")

    def record_assurance_score(self, tenant_id: str, score: float) -> None:
        if PROMETHEUS_AVAILABLE:
            try:
                UNIFIED_INTELLIGENCE_ASSURANCE_SCORE_GAUGE.labels(tenant_id=tenant_id).set(score)
            except Exception as e:
                logger.debug(f"Failed to record Prometheus metric: {e}")
