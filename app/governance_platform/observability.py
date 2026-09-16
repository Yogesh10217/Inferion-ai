"""Governance Platform Prometheus & OpenTelemetry Metrics Collector."""

import logging

try:
    from prometheus_client import Counter, Gauge
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False

logger = logging.getLogger(__name__)

if PROMETHEUS_AVAILABLE:
    GOVERNANCE_EVALUATIONS_TOTAL = Counter("ai_governance_policy_evaluations_total", "Total policy evaluations", ["tenant_id", "decision"])
    GOVERNANCE_VIOLATIONS_TOTAL = Counter("ai_governance_policy_violations_total", "Total governance violations", ["tenant_id", "severity"])
    GOVERNANCE_RISK_SCORE = Gauge("ai_governance_risk_score", "Average risk score", ["tenant_id"])
    GOVERNANCE_COMPLIANCE_SCORE = Gauge("ai_governance_compliance_score", "Compliance score percentage", ["tenant_id", "framework"])
    GOVERNANCE_APPROVAL_REQUIRED = Counter("ai_governance_approval_required_total", "Total actions requiring approval", ["tenant_id"])
    GOVERNANCE_REMEDIATIONS_TOTAL = Counter("ai_governance_remediations_total", "Total control enforcement remediations", ["tenant_id", "action"])
    GOVERNANCE_EVIDENCE_TOTAL = Counter("ai_governance_evidence_collected_total", "Total evidence records collected", ["tenant_id", "source"])
    GOVERNANCE_TRUST_SCORE = Gauge("ai_governance_trust_score", "Internal AI trust score", ["tenant_id"])


class GovernanceMetricsCollector:
    """Collects and exposes Prometheus metrics for the Governance Platform."""

    def record_evaluation(self, tenant_id: str, decision: str) -> None:
        if PROMETHEUS_AVAILABLE:
            try:
                GOVERNANCE_EVALUATIONS_TOTAL.labels(tenant_id=tenant_id, decision=decision).inc()
            except Exception:
                pass

    def record_violation(self, tenant_id: str, severity: str) -> None:
        if PROMETHEUS_AVAILABLE:
            try:
                GOVERNANCE_VIOLATIONS_TOTAL.labels(tenant_id=tenant_id, severity=severity).inc()
            except Exception:
                pass

    def record_risk_score(self, tenant_id: str, score: float) -> None:
        if PROMETHEUS_AVAILABLE:
            try:
                GOVERNANCE_RISK_SCORE.labels(tenant_id=tenant_id).set(score)
            except Exception:
                pass
