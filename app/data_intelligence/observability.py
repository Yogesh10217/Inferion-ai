"""Prometheus metrics collector for Data Intelligence Platform (Phase 5.43)."""

import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


class DataIntelligenceMetricsCollector:
    """Prometheus metrics collector prefixed with ai_data_*."""

    def __init__(self) -> None:
        self._counters: Dict[str, int] = {
            "ai_data_anomalies_total": 0,
            "ai_data_incidents_total": 0,
            "ai_data_pipeline_failures": 0,
            "ai_data_schema_changes": 0,
        }
        self._gauges: Dict[str, float] = {
            "ai_data_quality_score": 1.0,
            "ai_data_freshness_score": 1.0,
            "ai_data_trust_score": 100.0,
        }

    def increment(self, metric_name: str, value: int = 1) -> None:
        key = f"ai_data_{metric_name}" if not metric_name.startswith("ai_data_") else metric_name
        if key in self._counters:
            self._counters[key] += value
        else:
            self._counters[key] = value

    def set_gauge(self, metric_name: str, value: float) -> None:
        key = f"ai_data_{metric_name}" if not metric_name.startswith("ai_data_") else metric_name
        self._gauges[key] = value

    def get_metrics_summary(self) -> Dict[str, Any]:
        return {
            "counters": self._counters.copy(),
            "gauges": self._gauges.copy(),
        }
