"""
Operational Dashboard Model for Phase 5.68.
Provides unified snapshot models for telemetry visualizers, dashboards, and diagnostics endpoints.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict

from app.deployment.secrets import SecretsSanitizer


@dataclass
class OperationalDashboardSnapshot:
    timestamp: str
    platform_status: str
    availability: float
    error_rate: float
    latency_p50: float
    latency_p95: float
    latency_p99: float
    slo_status_counts: Dict[str, int]
    error_budget_status: str
    active_alerts_count: int
    active_incidents_count: int
    deployment_health_score: float
    dependency_status: Dict[str, str]
    certification_status: str
    evidence_level: str
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "platform_status": self.platform_status,
            "availability": self.availability,
            "error_rate": self.error_rate,
            "latency_p50": self.latency_p50,
            "latency_p95": self.latency_p95,
            "latency_p99": self.latency_p99,
            "slo_status_counts": self.slo_status_counts,
            "error_budget_status": self.error_budget_status,
            "active_alerts_count": self.active_alerts_count,
            "active_incidents_count": self.active_incidents_count,
            "deployment_health_score": self.deployment_health_score,
            "dependency_status": self.dependency_status,
            "certification_status": self.certification_status,
            "evidence_level": self.evidence_level,
            "details": SecretsSanitizer.sanitize_structure(self.details),
        }
