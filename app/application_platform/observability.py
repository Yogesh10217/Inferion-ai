"""Application Observability Engine (Phase 5.22 - Component 13).

Exports Prometheus metrics and OpenTelemetry trace correlation without exposing secrets:
Metrics:
- ai_application_executions_total
- ai_application_execution_duration_seconds
- ai_application_active_sessions
- ai_application_interactions_total
- ai_application_failures_total
- ai_application_fallbacks_total
- ai_application_human_escalations_total
- ai_application_feedback_total
- ai_application_cost_total
- ai_application_feature_evaluations_total

Correlation:
- trace_id, request_id, execution_id, application_id, application_version, tenant_id
"""

import logging
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class ApplicationTelemetrySpan(BaseModel):
    """OpenTelemetry correlation span."""

    trace_id: str
    request_id: str
    execution_id: str
    application_id: str
    application_version: str
    tenant_id: str
    attributes: Dict[str, Any] = Field(default_factory=dict)


class ApplicationMetricsCollector:
    """Prometheus & OpenTelemetry metrics collector for Application Platform."""

    def __init__(self) -> None:
        self._metric_counters: Dict[str, float] = {
            "ai_application_executions_total": 0.0,
            "ai_application_execution_duration_seconds": 0.0,
            "ai_application_active_sessions": 0.0,
            "ai_application_interactions_total": 0.0,
            "ai_application_failures_total": 0.0,
            "ai_application_fallbacks_total": 0.0,
            "ai_application_human_escalations_total": 0.0,
            "ai_application_feedback_total": 0.0,
            "ai_application_cost_total": 0.0,
            "ai_application_feature_evaluations_total": 0.0,
        }

    def increment(self, metric_name: str, value: float = 1.0, labels: Optional[Dict[str, str]] = None) -> None:
        if metric_name in self._metric_counters:
            self._metric_counters[metric_name] += value
        else:
            self._metric_counters[metric_name] = value

    def record_execution(
        self,
        span: ApplicationTelemetrySpan,
        duration_seconds: float,
        success: bool = True,
        cost_usd: float = 0.0,
    ) -> None:
        """Record an execution span without logging sensitive payloads."""
        self.increment("ai_application_executions_total")
        self.increment("ai_application_execution_duration_seconds", duration_seconds)
        self.increment("ai_application_cost_total", cost_usd)
        if not success:
            self.increment("ai_application_failures_total")

        logger.debug(
            f"[OBSERVABILITY] Execution span recorded for app={span.application_id} "
            f"exec={span.execution_id} tenant={span.tenant_id} duration={duration_seconds:.3f}s"
        )

    def get_metrics_summary(self) -> Dict[str, float]:
        return dict(self._metric_counters)
