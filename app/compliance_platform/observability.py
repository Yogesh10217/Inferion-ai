"""Prometheus Telemetry Collector for Compliance Platform."""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class ComplianceMetricsCollector:
    """Collects & exposes Compliance Platform Prometheus metrics without leaking secrets."""

    def __init__(self) -> None:
        self._counters: Dict[str, int] = {
            "ai_compliance_assessments_total": 0,
            "ai_compliance_assessment_failures_total": 0,
            "ai_compliance_control_failures_total": 0,
            "ai_compliance_open_findings": 0,
            "ai_compliance_evidence_expired_total": 0,
            "ai_compliance_evidence_missing_total": 0,
            "ai_compliance_remediation_total": 0,
            "ai_compliance_remediation_failures_total": 0,
            "ai_compliance_approval_required_total": 0,
            "ai_compliance_assurance_reports_total": 0,
        }
        self._gauges: Dict[str, float] = {
            "ai_compliance_posture_score": 100.0,
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
