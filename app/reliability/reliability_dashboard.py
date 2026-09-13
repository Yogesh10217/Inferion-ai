"""
Phase 5.70 - Reliability Dashboard Module.

Aggregates platform reliability metrics, resilience scores, SRE signals, recovery readiness, chaos experiment status, and evidence levels into a unified snapshot.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from app.reliability.reliability_models import ReliabilityStatus
from app.reliability.reliability_evidence import ReliabilityEvidenceLevel


@dataclass
class ReliabilityDashboardSnapshot:
    overall_status: ReliabilityStatus
    reliability_score: float
    resilience_score: float
    slo_status: str
    error_budget_remaining_percentage: float
    active_incidents_count: int
    active_alerts_count: int
    open_security_risks_count: int
    dependency_health_status: str
    recovery_status: str
    chaos_experiment_status: str
    disaster_recovery_readiness_status: str
    certification_decision: str
    auto_execution_blocked: bool
    evidence_level: ReliabilityEvidenceLevel
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "overall_status": self.overall_status.value,
            "reliability_score": self.reliability_score,
            "resilience_score": self.resilience_score,
            "slo_status": self.slo_status,
            "error_budget_remaining_percentage": self.error_budget_remaining_percentage,
            "active_incidents_count": self.active_incidents_count,
            "active_alerts_count": self.active_alerts_count,
            "open_security_risks_count": self.open_security_risks_count,
            "dependency_health_status": self.dependency_health_status,
            "recovery_status": self.recovery_status,
            "chaos_experiment_status": self.chaos_experiment_status,
            "disaster_recovery_readiness_status": self.disaster_recovery_readiness_status,
            "certification_decision": self.certification_decision,
            "auto_execution_blocked": self.auto_execution_blocked,
            "evidence_level": self.evidence_level.value,
            "details": self.details,
        }
