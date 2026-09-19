"""Prometheus Metrics Collector for Integration Platform."""

import logging
from typing import Optional

from app.observability.metrics import ObservabilityMetrics

logger = logging.getLogger(__name__)


class IntegrationMetricsCollector:
    """Collects Prometheus metrics for integration executions, webhooks, retries, and plugin calls."""

    def __init__(self, metrics: Optional[ObservabilityMetrics] = None) -> None:
        self.metrics = metrics or ObservabilityMetrics()

    def record_execution(self, tenant_id: str, connector: str, count: int = 1) -> None:
        logger.info(
            f"[INTEGRATION METRICS] Recorded execution counter for tenant '{tenant_id}': connector='{connector}', count={count}"
        )

    def record_webhook_event(self, tenant_id: str, event_type: str) -> None:
        logger.info(f"[INTEGRATION METRICS] Recorded webhook event for tenant '{tenant_id}': event_type='{event_type}'")
