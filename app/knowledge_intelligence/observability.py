"""Knowledge Observability Subsystem (Phase 5.35)."""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class KnowledgeMetricsCollector:
    """Collects Prometheus-formatted metrics prefixed with ai_knowledge_* without high-cardinality labels."""

    def __init__(self) -> None:
        self._counters: Dict[str, int] = {
            "ai_knowledge_retrieval_total": 0,
            "ai_knowledge_retrieval_blocked_total": 0,
            "ai_knowledge_contradictions_total": 0,
            "ai_knowledge_stale_records_total": 0,
            "ai_knowledge_provenance_validation_total": 0,
            "ai_knowledge_recommendations_total": 0,
        }

    def increment(self, metric_name: str, count: int = 1) -> None:
        if metric_name in self._counters:
            self._counters[metric_name] += count
        else:
            self._counters[metric_name] = count

    def get_metrics(self) -> Dict[str, int]:
        return dict(self._counters)
