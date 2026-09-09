"""Capacity intelligence metrics collector for Capacity Intelligence (Phase 5.56)."""

import logging
from typing import Dict

logger = logging.getLogger(__name__)


class CapacityIntelligenceMetricsCollector:
    """Collects Prometheus metrics with prefix ai_capacity_intelligence_*."""

    def __init__(self) -> None:
        self._counters: Dict[str, int] = {
            "ai_capacity_intelligence_assessments_total": 0,
            "ai_capacity_intelligence_forecasts_total": 0,
            "ai_capacity_intelligence_saturation_predictions_total": 0,
            "ai_capacity_intelligence_bottlenecks_total": 0,
            "ai_capacity_intelligence_recommendations_total": 0,
            "ai_capacity_intelligence_delegations_total": 0,
            "ai_capacity_intelligence_verification_total": 0,
            "ai_capacity_intelligence_isolation_violations_total": 0,
        }

    def increment(self, metric_name: str, value: int = 1) -> None:
        if metric_name in self._counters:
            self._counters[metric_name] += value
        else:
            self._counters[metric_name] = value

    def get_metrics(self) -> Dict[str, int]:
        return self._counters.copy()
