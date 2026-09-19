"""Prometheus metrics using ai_operations_* naming conventions."""

try:
    from prometheus_client import Counter, Gauge

    AI_OPERATIONS_SERVICES_TOTAL = Gauge(
        "ai_operations_services_total",
        "Total number of registered enterprise services.",
        ["tenant_id"],
    )
    AI_OPERATIONS_INCIDENTS_TOTAL = Counter(
        "ai_operations_incidents_total",
        "Total operational incidents created.",
        ["tenant_id", "severity"],
    )
    AI_OPERATIONS_ANOMALIES_TOTAL = Counter(
        "ai_operations_anomalies_total",
        "Total operational anomalies detected.",
        ["tenant_id", "category"],
    )
    AI_OPERATIONS_ASSURANCE_SCORE = Gauge(
        "ai_operations_assurance_score",
        "Current operational assurance score.",
        ["tenant_id", "service_id"],
    )
    AI_OPERATIONS_CAPACITY_RISK = Gauge(
        "ai_operations_capacity_risk",
        "Capacity risk level score.",
        ["tenant_id", "service_id", "resource_type"],
    )
    AI_OPERATIONS_DELEGATIONS_TOTAL = Counter(
        "ai_operations_delegations_total",
        "Total operational execution delegations.",
        ["tenant_id", "action_type"],
    )
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False


class OperationsObservabilityEngine:
    """Manages operational Prometheus metrics collection using ai_operations_* metrics."""

    def __init__(self) -> None:
        pass

    def record_service_count(self, tenant_id: str, count: int) -> None:
        if PROMETHEUS_AVAILABLE:
            AI_OPERATIONS_SERVICES_TOTAL.labels(tenant_id=tenant_id).set(count)

    def record_incident(self, tenant_id: str, severity: str) -> None:
        if PROMETHEUS_AVAILABLE:
            AI_OPERATIONS_INCIDENTS_TOTAL.labels(tenant_id=tenant_id, severity=severity).inc()

    def record_anomaly(self, tenant_id: str, category: str) -> None:
        if PROMETHEUS_AVAILABLE:
            AI_OPERATIONS_ANOMALIES_TOTAL.labels(tenant_id=tenant_id, category=category).inc()

    def record_assurance_score(self, tenant_id: str, service_id: str, score: float) -> None:
        if PROMETHEUS_AVAILABLE:
            AI_OPERATIONS_ASSURANCE_SCORE.labels(tenant_id=tenant_id, service_id=service_id).set(score)

    def record_delegation(self, tenant_id: str, action_type: str) -> None:
        if PROMETHEUS_AVAILABLE:
            AI_OPERATIONS_DELEGATIONS_TOTAL.labels(tenant_id=tenant_id, action_type=action_type).inc()
