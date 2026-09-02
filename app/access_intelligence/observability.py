"""Access Intelligence Observability & Prometheus Metrics (Phase 5.39)."""

from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class AccessMetricsCollector:
    """Collects Prometheus metrics for Access Intelligence using `ai_access_*` prefix.
    
    NEVER exposes secrets, raw authorization tokens, or sensitive identity metadata.
    """

    def __init__(self) -> None:
        self._counters: Dict[str, int] = {
            "ai_access_authorization_requests_total": 0,
            "ai_access_privileged_requests_total": 0,
            "ai_access_anomalies_total": 0,
            "ai_access_reviews_total": 0,
            "ai_access_certifications_total": 0,
            "ai_access_remediation_total": 0,
            "ai_access_emergency_requests_total": 0,
            "ai_access_toxic_combinations_total": 0,
        }

    def increment(self, metric_name: str, value: int = 1) -> None:
        if not metric_name.startswith("ai_access_"):
            metric_name = f"ai_access_{metric_name}"
        if metric_name not in self._counters:
            self._counters[metric_name] = 0
        self._counters[metric_name] += value
        logger.debug(f"[METRIC] {metric_name} += {value} (Total: {self._counters[metric_name]})")

    def get_metrics_summary(self) -> Dict[str, int]:
        return dict(self._counters)
