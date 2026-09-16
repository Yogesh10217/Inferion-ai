"""Prometheus Lifecycle Observability Subsystem (Phase 5.33)."""

import logging

from prometheus_client import Counter

from app.platform_contracts.observability import SafeMetricLabelSanitizer

logger = logging.getLogger(__name__)

LIFECYCLE_PROMOTIONS_TOTAL = Counter("ai_lifecycle_model_promotions_total", "Total model promotions executed", ["target", "tenant_id"])
LIFECYCLE_EVALUATIONS_TOTAL = Counter("ai_lifecycle_evaluation_runs_total", "Total evaluation runs executed", ["status", "tenant_id"])
LIFECYCLE_GATE_FAILURES_TOTAL = Counter("ai_lifecycle_gate_failures_total", "Total lifecycle gate failures", ["gate_type", "tenant_id"])
LIFECYCLE_DRIFT_EVENTS_TOTAL = Counter("ai_lifecycle_drift_events_total", "Total drift events detected", ["drift_type", "tenant_id"])
LIFECYCLE_ROLLBACKS_TOTAL = Counter("ai_lifecycle_rollbacks_total", "Total rollbacks requested", ["tenant_id"])
LIFECYCLE_RETIREMENTS_TOTAL = Counter("ai_lifecycle_retirements_total", "Total asset retirements finalized", ["tenant_id"])


class LifecycleMetricsCollector:
    """Collects AI asset lifecycle metrics following standard ai_lifecycle_* conventions."""

    def record_promotion(self, target: str, tenant_id: str) -> None:
        labels = SafeMetricLabelSanitizer.sanitize_labels({"target": target, "tenant_id": tenant_id})
        LIFECYCLE_PROMOTIONS_TOTAL.labels(target=labels["target"], tenant_id=labels["tenant_id"]).inc()

    def record_evaluation(self, status: str, tenant_id: str) -> None:
        labels = SafeMetricLabelSanitizer.sanitize_labels({"status": status, "tenant_id": tenant_id})
        LIFECYCLE_EVALUATIONS_TOTAL.labels(status=labels["status"], tenant_id=labels["tenant_id"]).inc()

    def record_gate_failure(self, gate_type: str, tenant_id: str) -> None:
        labels = SafeMetricLabelSanitizer.sanitize_labels({"gate_type": gate_type, "tenant_id": tenant_id})
        LIFECYCLE_GATE_FAILURES_TOTAL.labels(gate_type=labels["gate_type"], tenant_id=labels["tenant_id"]).inc()

    def record_drift(self, drift_type: str, tenant_id: str) -> None:
        labels = SafeMetricLabelSanitizer.sanitize_labels({"drift_type": drift_type, "tenant_id": tenant_id})
        LIFECYCLE_DRIFT_EVENTS_TOTAL.labels(drift_type=labels["drift_type"], tenant_id=labels["tenant_id"]).inc()

    def record_rollback(self, tenant_id: str) -> None:
        labels = SafeMetricLabelSanitizer.sanitize_labels({"tenant_id": tenant_id})
        LIFECYCLE_ROLLBACKS_TOTAL.labels(tenant_id=labels["tenant_id"]).inc()

    def record_retirement(self, tenant_id: str) -> None:
        labels = SafeMetricLabelSanitizer.sanitize_labels({"tenant_id": tenant_id})
        LIFECYCLE_RETIREMENTS_TOTAL.labels(tenant_id=labels["tenant_id"]).inc()
