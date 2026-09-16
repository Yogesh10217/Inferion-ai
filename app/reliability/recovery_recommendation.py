"""
Phase 5.70 - Recovery Recommendation Engine Module.

Generates safe, non-destructive recovery recommendations.
All destructive actions strictly enforce auto_execution_blocked = True.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict

from app.reliability.reliability_evidence import ReliabilityEvidenceLevel


class RecoveryAction(str, Enum):
    MONITOR = "MONITOR"
    INVESTIGATE = "INVESTIGATE"
    RESTART_RECOMMENDED = "RESTART_RECOMMENDED"
    ROLLBACK_RECOMMENDED = "ROLLBACK_RECOMMENDED"
    RESTORE_RECOMMENDED = "RESTORE_RECOMMENDED"
    FAILOVER_RECOMMENDED = "FAILOVER_RECOMMENDED"
    MANUAL_INTERVENTION_REQUIRED = "MANUAL_INTERVENTION_REQUIRED"
    BLOCK_RELEASE = "BLOCK_RELEASE"


@dataclass
class RecoveryRecommendation:
    action: RecoveryAction
    auto_execution_blocked: bool = True
    reason: str = ""
    severity: str = "MEDIUM"
    details: Dict[str, Any] = field(default_factory=dict)


class RecoveryRecommendationEngine:
    """Evaluates incident signals and generates non-destructive recovery recommendations."""

    def __init__(self, evidence_level: ReliabilityEvidenceLevel = ReliabilityEvidenceLevel.SIMULATION_RUNTIME) -> None:
        self.evidence_level = evidence_level

    def generate_recommendation(
        self,
        incident_severity: str = "LOW",
        database_failed: bool = False,
        primary_region_failed: bool = False,
        deployment_failed: bool = False,
        tampering_detected: bool = False,
        approved_runtime_target: bool = False,
    ) -> RecoveryRecommendation:
        blocked = not approved_runtime_target  # Default to auto_execution_blocked = True

        if tampering_detected or incident_severity == "CRITICAL_SECURITY":
            return RecoveryRecommendation(
                action=RecoveryAction.BLOCK_RELEASE,
                auto_execution_blocked=True,
                reason="Tampering or critical security threat detected. Release and operations blocked.",
                severity="CRITICAL",
            )
        elif primary_region_failed:
            return RecoveryRecommendation(
                action=RecoveryAction.FAILOVER_RECOMMENDED,
                auto_execution_blocked=blocked,
                reason="Primary region outage detected. Region failover recommended.",
                severity="CRITICAL",
            )
        elif database_failed:
            return RecoveryRecommendation(
                action=RecoveryAction.RESTORE_RECOMMENDED,
                auto_execution_blocked=blocked,
                reason="Database failure detected. Database restore recommended.",
                severity="HIGH",
            )
        elif deployment_failed:
            return RecoveryRecommendation(
                action=RecoveryAction.ROLLBACK_RECOMMENDED,
                auto_execution_blocked=blocked,
                reason="Deployment failure detected. Rollback recommended.",
                severity="HIGH",
            )
        elif incident_severity == "HIGH":
            return RecoveryRecommendation(
                action=RecoveryAction.MANUAL_INTERVENTION_REQUIRED,
                auto_execution_blocked=True,
                reason="High-severity incident requires operator manual intervention.",
                severity="HIGH",
            )
        elif incident_severity == "MEDIUM":
            return RecoveryRecommendation(
                action=RecoveryAction.INVESTIGATE,
                auto_execution_blocked=True,
                reason="Medium-severity signal detected. Investigation recommended.",
                severity="MEDIUM",
            )
        else:
            return RecoveryRecommendation(
                action=RecoveryAction.MONITOR,
                auto_execution_blocked=True,
                reason="System operating within normal parameters. Continue monitoring.",
                severity="LOW",
            )
