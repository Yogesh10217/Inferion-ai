"""
Phase 5.70 - Reliability Dashboard Module.

Aggregates platform reliability metrics, availability, SRE signals, recovery readiness, and evidence levels into a unified dashboard snapshot.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from app.reliability.reliability_engine import ReliabilityStatus
from app.reliability.reliability_evidence import ReliabilityEvidenceLevel


@dataclass
class ReliabilityDashboardSnapshot:
    overall_status: ReliabilityStatus
    overall_score: float
    availability_percentage: float
    active_incidents_count: int
    active_alerts_count: int
    slo_status: str
    error_budget_remaining_percentage: float
    recovery_readiness_status: str
    backup_readiness_status: str
    failover_readiness_status: str
    business_continuity_status: str
    latest_recovery_action: str
    auto_execution_blocked: bool
    evidence_level: ReliabilityEvidenceLevel
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "overall_status": self.overall_status.value,
            "overall_score": self.overall_score,
            "availability_percentage": self.availability_percentage,
            "active_incidents_count": self.active_incidents_count,
            "active_alerts_count": self.active_alerts_count,
            "slo_status": self.slo_status,
            "error_budget_remaining_percentage": self.error_budget_remaining_percentage,
            "recovery_readiness_status": self.recovery_readiness_status,
            "backup_readiness_status": self.backup_readiness_status,
            "failover_readiness_status": self.failover_readiness_status,
            "business_continuity_status": self.business_continuity_status,
            "latest_recovery_action": self.latest_recovery_action,
            "auto_execution_blocked": self.auto_execution_blocked,
            "evidence_level": self.evidence_level.value,
            "details": self.details,
        }
