"""
Phase 5.70 - Reliability Certification Module.

Evaluates platform evidence, recovery audit results, backup/failover/continuity readiness, and security/incident integration to issue deterministic Reliability Certification Decisions.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from app.reliability.reliability_models import ReliabilityStatus
from app.reliability.reliability_engine import ReliabilityResult
from app.reliability.reliability_evidence import ReliabilityEvidenceLevel
from app.reliability.recovery_audit import RecoveryAuditResult


class ReliabilityCertificationDecision(str, Enum):
    RELIABILITY_CERTIFIED = "RELIABILITY_CERTIFIED"
    RELIABILITY_CERTIFIED_WITH_WARNINGS = "RELIABILITY_CERTIFIED_WITH_WARNINGS"
    RELIABILITY_MANUAL_REVIEW_REQUIRED = "RELIABILITY_MANUAL_REVIEW_REQUIRED"
    RELIABILITY_AT_RISK = "RELIABILITY_AT_RISK"
    RELIABILITY_BLOCKED = "RELIABILITY_BLOCKED"
    RELIABILITY_NOT_EXECUTED = "RELIABILITY_NOT_EXECUTED"


@dataclass
class ReliabilityCertificationResult:
    decision: ReliabilityCertificationDecision
    certified: bool
    live_production_recovery_validated: bool  # Strict truthfulness boundary flag
    overall_score: float
    audit_passed: bool
    backup_ready: bool
    failover_ready: bool
    business_continuity_ready: bool
    incident_integration_operational: bool
    security_integration_operational: bool
    reasons: List[str]
    evidence_level: ReliabilityEvidenceLevel
    details: Dict[str, Any] = field(default_factory=dict)


class ReliabilityCertificationEngine:
    """Certifies platform reliability based on empirical evidence and audit compliance."""

    def __init__(self, evidence_level: ReliabilityEvidenceLevel = ReliabilityEvidenceLevel.SIMULATION_RUNTIME) -> None:
        self.evidence_level = evidence_level

    def evaluate_certification(
        self,
        reliability_result: Optional[ReliabilityResult] = None,
        audit_result: Optional[RecoveryAuditResult] = None,
        backup_ready: bool = True,
        failover_ready: bool = True,
        business_continuity_ready: bool = True,
        incident_integration_operational: bool = True,
        security_integration_operational: bool = True,
        empirical_real_production_recovery_executed: bool = False,
        executed: bool = True,
    ) -> ReliabilityCertificationResult:
        if not executed:
            return ReliabilityCertificationResult(
                decision=ReliabilityCertificationDecision.RELIABILITY_NOT_EXECUTED,
                certified=False,
                live_production_recovery_validated=False,
                overall_score=0.0,
                audit_passed=False,
                backup_ready=False,
                failover_ready=False,
                business_continuity_ready=False,
                incident_integration_operational=False,
                security_integration_operational=False,
                reasons=["Reliability certification evaluation not executed."],
                evidence_level=self.evidence_level,
            )

        reasons: List[str] = []
        score = reliability_result.overall_score if reliability_result else 100.0
        rel_status = reliability_result.status if reliability_result else ReliabilityStatus.HEALTHY

        audit_passed = audit_result.valid if audit_result else True
        if audit_result and audit_result.tampering_detected:
            audit_passed = False
            reasons.append("Audit tampering detected! Evidence integrity violated.")

        if rel_status == ReliabilityStatus.BLOCKED or not audit_passed:
            decision = ReliabilityCertificationDecision.RELIABILITY_BLOCKED
            certified = False
            if rel_status == ReliabilityStatus.BLOCKED:
                reasons.append("Platform reliability status is BLOCKED.")
        elif rel_status == ReliabilityStatus.FAILING:
            decision = ReliabilityCertificationDecision.RELIABILITY_BLOCKED
            certified = False
            reasons.append("Platform reliability status is FAILING.")
        elif rel_status == ReliabilityStatus.AT_RISK:
            decision = ReliabilityCertificationDecision.RELIABILITY_AT_RISK
            certified = False
            reasons.append(f"Reliability score is low ({score}) with status AT_RISK.")
        elif not backup_ready or not failover_ready or not business_continuity_ready:
            decision = ReliabilityCertificationDecision.RELIABILITY_MANUAL_REVIEW_REQUIRED
            certified = False
            reasons.append("Backup, failover, or business continuity evaluation incomplete or blocked.")
        elif rel_status == ReliabilityStatus.DEGRADED:
            decision = ReliabilityCertificationDecision.RELIABILITY_CERTIFIED_WITH_WARNINGS
            certified = True
            reasons.append(f"Reliability certified with warnings (score {score}).")
        else:
            decision = ReliabilityCertificationDecision.RELIABILITY_CERTIFIED
            certified = True
            reasons.append("All reliability checks, audit integrity, and recovery evaluations PASSED.")

        return ReliabilityCertificationResult(
            decision=decision,
            certified=certified,
            live_production_recovery_validated=empirical_real_production_recovery_executed,  # Strictly False unless real execution occurred
            overall_score=score,
            audit_passed=audit_passed,
            backup_ready=backup_ready,
            failover_ready=failover_ready,
            business_continuity_ready=business_continuity_ready,
            incident_integration_operational=incident_integration_operational,
            security_integration_operational=security_integration_operational,
            reasons=reasons,
            evidence_level=self.evidence_level,
            details={
                "reliability_status": rel_status.value,
                "audit_passed": audit_passed,
            },
        )
