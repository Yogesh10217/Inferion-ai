"""Prometheus Metrics Collector for Data Governance Subsystem."""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class DataGovernanceMetricsCollector:
    """Collects & exposes telemetry without exposing raw secrets, PII, or cross-tenant data."""

    def __init__(self) -> None:
        self._counters: Dict[str, int] = {
            "ai_data_governance_assets_total": 0,
            "ai_data_governance_access_requests_total": 0,
            "ai_data_governance_access_denied_total": 0,
            "ai_data_governance_quality_violations_total": 0,
            "ai_data_governance_contract_violations_total": 0,
            "ai_data_governance_consent_violations_total": 0,
            "ai_data_governance_retention_actions_total": 0,
        }
        self._gauges: Dict[str, float] = {
            "ai_data_governance_trust_score": 100.0,
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
