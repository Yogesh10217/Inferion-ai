"""Prometheus Telemetry Collector for Decision Intelligence Platform."""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class DecisionMetricsCollector:
    """Collects & exposes Decision Intelligence Prometheus metrics without leaking secrets."""

    def __init__(self) -> None:
        self._counters: Dict[str, int] = {
            "ai_decision_decisions_total": 0,
            "ai_decision_scenarios_total": 0,
            "ai_decision_recommendations_total": 0,
            "ai_decision_approvals_required_total": 0,
        }
        self._gauges: Dict[str, float] = {
            "ai_decision_trust_score": 90.0,
            "ai_decision_value_realized_ratio": 1.0,
        }

    def increment(self, metric_name: str, value: int = 1) -> None:
        if metric_name in self._counters:
            self._counters[metric_name] += value
        else:
            self._counters[metric_name] = value

    def set_gauge(self, metric_name: str, value: float) -> None:
        self._gauges[metric_name] = value

    def get_metrics_summary(self) -> Dict[str, Any]:
        return {
            "counters": dict(self._counters),
            "gauges": dict(self._gauges),
        }
