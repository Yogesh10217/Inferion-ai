"""Prometheus Observability Metrics for Model Intelligence (Phase 5.44)."""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class ModelIntelligenceMetricsCollector:
    """Collector for Prometheus metrics prefixed with ai_model_*.

    Must never expose secrets, tokens, raw prompts, or credentials.
    """

    def __init__(self) -> None:
        self._counters: Dict[str, float] = {
            "ai_model_evaluation_total": 0.0,
            "ai_model_drift_detected_total": 0.0,
            "ai_model_incidents_total": 0.0,
            "ai_model_remediation_total": 0.0,
        }
        self._gauges: Dict[str, float] = {
            "ai_model_trust_score": 100.0,
            "ai_model_assurance_score": 100.0,
        }

    def increment_counter(self, metric_name: str, value: float = 1.0) -> None:
        if not metric_name.startswith("ai_model_"):
            metric_name = f"ai_model_{metric_name}"
        if metric_name not in self._counters:
            self._counters[metric_name] = 0.0
        self._counters[metric_name] += value
        logger.debug(f"[MODEL METRICS] Counter {metric_name} += {value} -> {self._counters[metric_name]}")

    def set_gauge(self, metric_name: str, value: float) -> None:
        if not metric_name.startswith("ai_model_"):
            metric_name = f"ai_model_{metric_name}"
        self._gauges[metric_name] = value
        logger.debug(f"[MODEL METRICS] Gauge {metric_name} = {value}")

    def collect_metrics(self) -> Dict[str, Any]:
        return {
            "counters": dict(self._counters),
            "gauges": dict(self._gauges),
        }
