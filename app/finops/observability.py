"""FinOps Observability & Prometheus Metrics Integration."""

import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


class FinOpsMetricsCollector:
    """Prometheus metrics collector for FinOps financial intelligence events."""

    def __init__(self) -> None:
        self.metrics = {
            "ai_finops_cost_total": 0.0,
            "ai_finops_usage_total": 0,
            "ai_finops_budget_utilization_ratio": 0.0,
            "ai_finops_budget_exceeded_total": 0,
            "ai_finops_forecast_cost": 0.0,
            "ai_finops_anomalies_total": 0,
            "ai_finops_optimization_recommendations_total": 0,
            "ai_finops_optimizations_applied_total": 0,
            "ai_finops_estimated_savings_total": 0.0,
            "ai_finops_verified_savings_total": 0.0,
            "ai_finops_capacity_utilization_ratio": 0.0,
            "ai_finops_chargeback_total": 0.0,
        }

    def record_cost(self, cost_dollars: float) -> None:
        self.metrics["ai_finops_cost_total"] += cost_dollars
        self.metrics["ai_finops_usage_total"] += 1

    def increment(self, metric_name: str, value: float = 1.0) -> None:
        if metric_name in self.metrics:
            self.metrics[metric_name] += value
            logger.debug(f"[FINOPS METRICS] Incremented {metric_name} by {value} -> {self.metrics[metric_name]}")

    def get_summary(self) -> Dict[str, Any]:
        return dict(self.metrics)
