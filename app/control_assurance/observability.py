"""Prometheus-Compatible Control Assurance Metrics Subsystem (Phase 5.38)."""

import logging
from typing import Any, Dict

from app.platform_contracts.observability import MetricNameValidator, SafeMetricLabelSanitizer

logger = logging.getLogger(__name__)


class ControlAssuranceMetricsCollector:
    """Collects Prometheus metrics for Control Assurance subsystem."""

    def __init__(self) -> None:
        self.label_sanitizer = SafeMetricLabelSanitizer()
        self.metric_validator = MetricNameValidator()

        self._counters: Dict[str, float] = {
            "ai_control_assurance_evaluations_total": 0.0,
            "ai_control_assurance_violations_total": 0.0,
            "ai_control_assurance_attestations_total": 0.0,
            "ai_control_assurance_remediations_total": 0.0,
        }
        self._gauges: Dict[str, float] = {
            "ai_control_assurance_score": 100.0,
            "ai_control_assurance_active_controls": 0.0,
        }

    def increment_evaluations(self, tenant_id: str, status: str = "PASSED") -> None:
        key = "ai_control_assurance_evaluations_total"
        self._counters[key] += 1.0
        logger.debug(f"[METRIC] {key} incremented for tenant {tenant_id} with status {status}")

    def increment_violations(self, tenant_id: str, severity: str = "HIGH") -> None:
        key = "ai_control_assurance_violations_total"
        self._counters[key] += 1.0

    def increment_attestations(self, tenant_id: str) -> None:
        key = "ai_control_assurance_attestations_total"
        self._counters[key] += 1.0

    def set_assurance_score(self, tenant_id: str, score: float) -> None:
        key = "ai_control_assurance_score"
        self._gauges[key] = score

    def get_metrics_summary(self) -> Dict[str, Any]:
        return {
            "counters": dict(self._counters),
            "gauges": dict(self._gauges),
        }
