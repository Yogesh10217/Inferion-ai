"""Prometheus Metrics Collector for Marketplace Subsystem."""

import logging
from typing import Dict

logger = logging.getLogger(__name__)


class MarketplaceMetricsCollector:
    """Prometheus metrics mapper for publishers, marketplace items, reviews, and installations."""

    def __init__(self) -> None:
        self.metrics: Dict[str, float] = {
            "publishers_total": 0.0,
            "marketplace_items_total": 0.0,
            "marketplace_items_published_total": 0.0,
            "marketplace_reviews_total": 0.0,
            "marketplace_reviews_approved_total": 0.0,
            "marketplace_reviews_rejected_total": 0.0,
            "marketplace_installations_total": 0.0,
        }

    def increment(self, metric_name: str, value: float = 1.0) -> None:
        if metric_name in self.metrics:
            self.metrics[metric_name] += value
        else:
            self.metrics[metric_name] = value

    def get_metrics_summary(self) -> Dict[str, float]:
        return dict(self.metrics)
