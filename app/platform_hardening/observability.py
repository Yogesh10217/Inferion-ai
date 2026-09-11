"""
Prometheus Observability Metrics for Platform Hardening.
"""

from prometheus_client import Counter, Gauge

AUDITS_TOTAL = Counter(
    "ai_platform_hardening_audits_total",
    "Total platform hardening audit executions",
    ["tenant_id", "status"],
)

FINDINGS_TOTAL = Counter(
    "ai_platform_hardening_findings_total",
    "Total platform audit findings detected",
    ["tenant_id", "severity"],
)

CRITICAL_FINDINGS = Gauge(
    "ai_platform_hardening_critical_findings",
    "Current active critical findings count",
    ["tenant_id"],
)

PROVIDER_FAILURES = Counter(
    "ai_platform_hardening_provider_failures",
    "Total provider health failures",
    ["provider_id"],
)

TRACE_FAILURES = Counter(
    "ai_platform_hardening_trace_failures",
    "Total trace propagation failures",
    ["tenant_id"],
)

LINEAGE_FAILURES = Counter(
    "ai_platform_hardening_lineage_failures",
    "Total lineage validation failures",
    ["tenant_id"],
)

GOVERNANCE_FAILURES = Counter(
    "ai_platform_hardening_governance_failures",
    "Total governance validation failures",
    ["tenant_id"],
)

STUB_FINDINGS = Gauge(
    "ai_platform_hardening_stub_findings",
    "Current unclassified production stub count",
    ["tenant_id"],
)

DEPENDENCY_VIOLATIONS = Counter(
    "ai_platform_hardening_dependency_violations",
    "Total contract dependency violations",
    ["tenant_id"],
)

CERTIFICATION_STATUS = Gauge(
    "ai_platform_hardening_certification_status",
    "Platform certification readiness score",
    ["tenant_id", "status"],
)


class PlatformHardeningObservability:
    """Helper wrapper for recording Prometheus metrics."""

    @staticmethod
    def record_audit(tenant_id: str, status: str, findings_count: int, critical_count: int, score: float):
        AUDITS_TOTAL.labels(tenant_id=tenant_id, status=status).inc()
        CRITICAL_FINDINGS.labels(tenant_id=tenant_id).set(critical_count)
        CERTIFICATION_STATUS.labels(tenant_id=tenant_id, status=status).set(score)
