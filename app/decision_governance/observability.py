"""Prometheus observability exporter using ai_decision_* metric prefix."""

from prometheus_client import CollectorRegistry, Counter, Gauge


class DecisionGovernanceMetrics:
    """Manages Prometheus telemetry metrics for Decision Governance platform."""

    _instance = None

    def __new__(cls, registry: CollectorRegistry = None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_metrics(registry)
        return cls._instance

    def _init_metrics(self, registry: CollectorRegistry = None):
        reg = registry

        self.decisions_created = Counter(
            "ai_decision_created_total",
            "Total number of decisions created",
            ["tenant_id", "decision_type"],
            registry=reg,
        )

        self.decisions_recommended = Counter(
            "ai_decision_recommended_total",
            "Total number of decisions recommended",
            ["tenant_id"],
            registry=reg,
        )

        self.decisions_approved = Counter(
            "ai_decision_approved_total",
            "Total number of decisions approved",
            ["tenant_id"],
            registry=reg,
        )

        self.decisions_blocked = Counter(
            "ai_decision_blocked_total",
            "Total number of decisions blocked",
            ["tenant_id"],
            registry=reg,
        )

        self.decisions_conflicts = Counter(
            "ai_decision_conflicts_total",
            "Total number of decision conflicts detected",
            ["tenant_id", "conflict_type"],
            registry=reg,
        )

        self.decision_confidence = Gauge(
            "ai_decision_confidence",
            "Latest decision confidence score",
            ["tenant_id", "decision_id"],
            registry=reg,
        )

        self.decision_risk = Gauge(
            "ai_decision_risk",
            "Latest decision risk score",
            ["tenant_id", "decision_id"],
            registry=reg,
        )

        self.decision_assurance = Gauge(
            "ai_decision_assurance",
            "Latest decision assurance score",
            ["tenant_id", "decision_id"],
            registry=reg,
        )
