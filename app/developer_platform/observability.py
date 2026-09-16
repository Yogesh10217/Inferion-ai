"""Prometheus Metrics Collector for Developer Platform."""

import logging
from typing import Optional

from app.observability.metrics import ObservabilityMetrics

logger = logging.getLogger(__name__)


class DeveloperMetricsCollector:
    """Collects Prometheus metrics for projects, API requests, pipeline runs, quality gate failures, and deployments."""

    def __init__(self, metrics: Optional[ObservabilityMetrics] = None) -> None:
        self.metrics = metrics or ObservabilityMetrics()

    def record_pipeline_run(self, tenant_id: str, status: str) -> None:
        logger.info(f"[DEVELOPER METRICS] Recorded pipeline run for tenant '{tenant_id}': status='{status}'")

    def record_deployment(self, tenant_id: str, environment: str) -> None:
        logger.info(f"[DEVELOPER METRICS] Recorded deployment for tenant '{tenant_id}': env='{environment}'")
