"""Knowledge Assurance Observability Module.

Provides Prometheus metrics with mandatory ai_knowledge_* prefix.
"""

from typing import Any, Optional
from prometheus_client import REGISTRY, Counter, Gauge

PROMETHEUS_AVAILABLE = True


def _get_or_create_metric(metric_type: Any, name: str, description: str, labelnames: Optional[list] = None) -> Any:
    if not PROMETHEUS_AVAILABLE:
        return None
    try:
        # Check if already registered
        if hasattr(REGISTRY, "_names_to_collectors") and name in getattr(REGISTRY, "_names_to_collectors"):
            return getattr(REGISTRY, "_names_to_collectors")[name]
        return metric_type(name, description, labelnames=labelnames or [])
    except Exception:
        return None


class KnowledgeAssuranceMetrics:
    """Prometheus metrics collector for Knowledge Assurance with ai_knowledge_* prefix."""

    context_assemblies_total: Any
    conflicts_total: Any
    trust_score: Any
    stale_sources_total: Any
    assurance_score: Any

    def __init__(self) -> None:
        self.context_assemblies_total = _get_or_create_metric(
            Counter,
            "ai_knowledge_context_assemblies_total",
            "Total number of knowledge context assemblies performed",
            labelnames=["tenant_id", "status"],
        )
        self.conflicts_total = _get_or_create_metric(
            Counter,
            "ai_knowledge_conflicts_total",
            "Total number of knowledge conflicts detected",
            labelnames=["tenant_id", "severity"],
        )
        self.trust_score = _get_or_create_metric(
            Gauge,
            "ai_knowledge_trust_score",
            "Current average knowledge trust score",
            labelnames=["tenant_id"],
        )
        self.stale_sources_total = _get_or_create_metric(
            Gauge,
            "ai_knowledge_stale_sources_total",
            "Total number of stale knowledge sources",
            labelnames=["tenant_id"],
        )
        self.assurance_score = _get_or_create_metric(
            Gauge,
            "ai_knowledge_assurance_score",
            "Overall knowledge assurance score",
            labelnames=["tenant_id"],
        )

    def record_context_assembly(self, tenant_id: str, status: str = "SUCCESS") -> None:
        if self.context_assemblies_total:
            self.context_assemblies_total.labels(tenant_id=tenant_id, status=status).inc()

    def record_conflict_detected(self, tenant_id: str, severity: str = "MEDIUM") -> None:
        if self.conflicts_total:
            self.conflicts_total.labels(tenant_id=tenant_id, severity=severity).inc()

    def set_trust_score(self, tenant_id: str, score: float) -> None:
        if self.trust_score:
            self.trust_score.labels(tenant_id=tenant_id).set(score)

    def set_stale_sources_count(self, tenant_id: str, count: int) -> None:
        if self.stale_sources_total:
            self.stale_sources_total.labels(tenant_id=tenant_id).set(count)

    def set_assurance_score(self, tenant_id: str, score: float) -> None:
        if self.assurance_score:
            self.assurance_score.labels(tenant_id=tenant_id).set(score)
