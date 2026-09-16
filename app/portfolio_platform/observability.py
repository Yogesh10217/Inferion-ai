"""Prometheus Telemetry Collector for Portfolio Platform."""

import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


class PortfolioMetricsCollector:
    """Collects & exposes Portfolio Platform Prometheus metrics without leaking secrets."""

    def __init__(self) -> None:
        self._counters: Dict[str, int] = {
            "ai_portfolio_initiatives_total": 0,
            "ai_portfolio_investments_total": 0,
            "ai_portfolio_funding_requests_total": 0,
            "ai_portfolio_approval_required_total": 0,
            "ai_portfolio_optimization_total": 0,
        }
        self._gauges: Dict[str, float] = {
            "ai_portfolio_value_realization_ratio": 1.0,
            "ai_portfolio_budget_utilization": 0.0,
            "ai_portfolio_trust_score": 90.0,
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
