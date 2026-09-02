"""Operations Intelligence Observability & Prometheus Metrics (Phase 5.41)."""

from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class OperationsMetricsCollector:
    """Collects Prometheus metrics for Operations Intelligence using `ai_operations_*` prefix.
    
    NEVER exposes secrets, tokens, credentials, or sensitive incident metadata.
    """

    def __init__(self) -> None:
        self._counters: Dict[str, int] = {
            "ai_operations_alerts_ingested_total": 0,
            "ai_operations_incidents_created_total": 0,
            "ai_operations_major_incidents_total": 0,
            "ai_operations_remediations_delegated_total": 0,
            "ai_operations_governance_blocks_total": 0,
        }

    def increment(self, metric_name: str, value: int = 1) -> None:
        if not metric_name.startswith("ai_operations_"):
            metric_name = f"ai_operations_{metric_name}"
        if metric_name not in self._counters:
            self._counters[metric_name] = 0
        self._counters[metric_name] += value
        logger.debug(f"[METRIC] {metric_name} += {value} (Total: {self._counters[metric_name]})")

    def get_metrics_summary(self) -> Dict[str, int]:
        return dict(self._counters)
