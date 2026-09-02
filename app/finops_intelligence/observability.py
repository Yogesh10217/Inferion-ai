"""FinOps Observability & Prometheus Metrics (Phase 5.42)."""

from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class FinOpsMetricsCollector:
    """Collects Prometheus metrics for FinOps Intelligence using `ai_finops_*` prefix.
    
    NEVER exposes secrets, API keys, or sensitive billing metadata.
    """

    def __init__(self) -> None:
        self._counters: Dict[str, float] = {
            "ai_finops_cost_total": 0.0,
            "ai_finops_budget_utilization": 0.0,
            "ai_finops_anomalies_total": 0.0,
            "ai_finops_optimization_recommendations": 0.0,
            "ai_finops_forecast_accuracy": 100.0,
        }

    def increment(self, metric_name: str, value: float = 1.0) -> None:
        if not metric_name.startswith("ai_finops_"):
            metric_name = f"ai_finops_{metric_name}"
        if metric_name not in self._counters:
            self._counters[metric_name] = 0.0
        self._counters[metric_name] += value
        logger.debug(f"[METRIC] {metric_name} += {value} (Total: {self._counters[metric_name]})")

    def set_gauge(self, metric_name: str, value: float) -> None:
        if not metric_name.startswith("ai_finops_"):
            metric_name = f"ai_finops_{metric_name}"
        self._counters[metric_name] = value

    def get_metrics_summary(self) -> Dict[str, float]:
        return dict(self._counters)
