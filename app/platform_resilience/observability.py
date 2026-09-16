"""Resilience Observability & Prometheus Metrics Subsystem (Phase 5.37)."""

import logging
from typing import Dict

from app.platform_contracts.observability import MetricNameValidator, SafeMetricLabelSanitizer

logger = logging.getLogger(__name__)


class ResilienceMetricsCollector:
    """Collects and exposes sanitized Prometheus metrics following standard ai_resilience_* metric conventions."""

    def __init__(self) -> None:
        self.validator = MetricNameValidator()
        self.sanitizer = SafeMetricLabelSanitizer()
        self._counters: Dict[str, float] = {
            "ai_resilience_failovers_total": 0.0,
            "ai_resilience_recoveries_total": 0.0,
            "ai_resilience_capacity_saturations_total": 0.0,
            "ai_resilience_circuit_breaker_trips_total": 0.0,
            "ai_resilience_load_shed_events_total": 0.0,
        }

    def increment_failovers_total(self, tenant_id: str, status: str = "COMPLETED") -> None:
        self.sanitizer.sanitize_labels({"tenant_id": tenant_id, "status": status})
        self._counters["ai_resilience_failovers_total"] += 1.0

    def increment_recoveries_total(self, tenant_id: str, status: str = "RECOVERED") -> None:
        self.sanitizer.sanitize_labels({"tenant_id": tenant_id, "status": status})
        self._counters["ai_resilience_recoveries_total"] += 1.0

    def increment_capacity_saturations(self, tenant_id: str, resource_id: str) -> None:
        self.sanitizer.sanitize_labels({"tenant_id": tenant_id, "resource_id": resource_id})
        self._counters["ai_resilience_capacity_saturations_total"] += 1.0

    def increment_circuit_breaker_trips(self, tenant_id: str, breaker_id: str) -> None:
        self.sanitizer.sanitize_labels({"tenant_id": tenant_id, "breaker_id": breaker_id})
        self._counters["ai_resilience_circuit_breaker_trips_total"] += 1.0

    def get_metrics_summary(self) -> Dict[str, float]:
        return dict(self._counters)
