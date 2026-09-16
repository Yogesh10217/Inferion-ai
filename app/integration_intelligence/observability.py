"""Integration Intelligence Observability & Prometheus Metrics (Phase 5.40)."""

import logging
from typing import Dict

logger = logging.getLogger(__name__)


class IntegrationMetricsCollector:
    """Collects Prometheus metrics for Integration Intelligence using `ai_integration_*` prefix.

    NEVER exposes secrets, raw authorization tokens, or sensitive identity/payload metadata.
    """

    def __init__(self) -> None:
        self._counters: Dict[str, int] = {
            "ai_integration_workflow_requests_total": 0,
            "ai_integration_delegated_executions_total": 0,
            "ai_integration_failures_total": 0,
            "ai_integration_retries_total": 0,
            "ai_integration_verification_failures_total": 0,
            "ai_integration_recovery_events_total": 0,
            "ai_integration_governance_blocks_total": 0,
        }

    def increment(self, metric_name: str, value: int = 1) -> None:
        if not metric_name.startswith("ai_integration_"):
            metric_name = f"ai_integration_{metric_name}"
        if metric_name not in self._counters:
            self._counters[metric_name] = 0
        self._counters[metric_name] += value
        logger.debug(f"[METRIC] {metric_name} += {value} (Total: {self._counters[metric_name]})")

    def get_metrics_summary(self) -> Dict[str, int]:
        return dict(self._counters)
