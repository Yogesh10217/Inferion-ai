"""Agent Observability & Prometheus Metrics Subsystem (Phase 5.36)."""

import logging
from typing import Dict

from app.platform_contracts.observability import MetricNameValidator, SafeMetricLabelSanitizer

logger = logging.getLogger(__name__)


class AgentMetricsCollector:
    """Collects and exposes sanitized Prometheus metrics following standard ai_agents_* metric conventions."""

    def __init__(self) -> None:
        self.validator = MetricNameValidator()
        self.sanitizer = SafeMetricLabelSanitizer()
        self._counters: Dict[str, float] = {
            "ai_agents_tasks_total": 0.0,
            "ai_agents_autonomy_violations_total": 0.0,
            "ai_agents_tool_invocations_total": 0.0,
            "ai_agents_human_escalations_total": 0.0,
            "ai_agents_execution_duration_seconds": 0.0,
        }

    def increment_tasks_total(self, tenant_id: str, status: str = "COMPLETED") -> None:
        self.sanitizer.sanitize_labels({"tenant_id": tenant_id, "status": status})
        self._counters["ai_agents_tasks_total"] += 1.0

    def increment_autonomy_violations(self, tenant_id: str, violation_type: str) -> None:
        self.sanitizer.sanitize_labels({"tenant_id": tenant_id, "type": violation_type})
        self._counters["ai_agents_autonomy_violations_total"] += 1.0

    def increment_tool_invocations(self, tenant_id: str, tool_type: str) -> None:
        self.sanitizer.sanitize_labels({"tenant_id": tenant_id, "tool_type": tool_type})
        self._counters["ai_agents_tool_invocations_total"] += 1.0

    def increment_human_escalations(self, tenant_id: str, reason: str) -> None:
        self.sanitizer.sanitize_labels({"tenant_id": tenant_id, "reason": reason})
        self._counters["ai_agents_human_escalations_total"] += 1.0

    def observe_execution_duration(self, tenant_id: str, duration_sec: float) -> None:
        self.sanitizer.sanitize_labels({"tenant_id": tenant_id})
        self._counters["ai_agents_execution_duration_seconds"] += duration_sec

    def get_metrics_summary(self) -> Dict[str, float]:
        return dict(self._counters)
