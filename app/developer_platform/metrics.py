"""Prometheus Metrics Collector for Developer Platform Subsystem."""

import logging
from typing import Dict

logger = logging.getLogger(__name__)


class DeveloperPlatformMetricsCollector:
    """Prometheus metrics mapper for developers, projects, webhooks, and SDK validations."""

    def __init__(self) -> None:
        self.metrics: Dict[str, float] = {
            "developers_total": 0.0,
            "developers_active_total": 0.0,
            "developer_projects_total": 0.0,
            "webhook_subscriptions_total": 0.0,
            "webhook_deliveries_total": 0.0,
            "webhook_failures_total": 0.0,
            "developer_api_keys_issued_total": 0.0,
        }

    def increment(self, metric_name: str, value: float = 1.0) -> None:
        if metric_name in self.metrics:
            self.metrics[metric_name] += value
        else:
            self.metrics[metric_name] = value

    def get_metrics_summary(self) -> Dict[str, float]:
        return dict(self.metrics)
