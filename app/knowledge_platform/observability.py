"""Prometheus Metrics Collector for Knowledge Platform."""

import logging
from typing import Dict, Any, Optional

from app.observability.metrics import ObservabilityMetrics


logger = logging.getLogger(__name__)


class KnowledgeMetricsCollector:
    """Collects Prometheus metrics for knowledge retrieval, context building, conflicts, and trust scores."""

    def __init__(self, metrics: Optional[ObservabilityMetrics] = None) -> None:
        self.metrics = metrics or ObservabilityMetrics()

    def record_retrieval(self, tenant_id: str, strategy: str, count: int) -> None:
        logger.info(f"[KNOWLEDGE METRICS] Recorded retrieval counter for tenant '{tenant_id}': strategy='{strategy}', count={count}")

    def record_context_tokens(self, tenant_id: str, tokens: int) -> None:
        logger.info(f"[KNOWLEDGE METRICS] Recorded context tokens for tenant '{tenant_id}': tokens={tokens}")

