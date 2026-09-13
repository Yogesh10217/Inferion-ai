"""
Phase 5.70 - Security Recovery Integration Module.

Integrates Reliability Engineering with Phase 5.69 Security Operations.
Security events trigger recovery analysis and recommendations, but NEVER execute destructive recovery automatically.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from app.reliability.recovery_recommendation import RecoveryAction, RecoveryRecommendation, RecoveryRecommendationEngine
from app.reliability.reliability_evidence import ReliabilityEvidenceLevel
from app.reliability.recovery_state_machine import RecoveryState, RecoveryStateMachine
from app.security_operations import SecurityOperationsOrchestrator


@dataclass
class SecurityRecoveryResult:
    threat_detected: bool
    recovery_state_entered: RecoveryState
    recommendation: RecoveryRecommendation
    auto_execution_blocked: bool
    evidence_level: ReliabilityEvidenceLevel
    details: Dict[str, Any] = field(default_factory=dict)


class SecurityRecoveryIntegration:
    """Correlates security threats with reliability recovery state machine and non-destructive recommendations."""

    def __init__(
        self,
        security_orchestrator: Optional[SecurityOperationsOrchestrator] = None,
        evidence_level: ReliabilityEvidenceLevel = ReliabilityEvidenceLevel.SIMULATION_RUNTIME,
    ) -> None:
        self.security_orchestrator = security_orchestrator or SecurityOperationsOrchestrator()
        self.recommendation_engine = RecoveryRecommendationEngine(evidence_level=evidence_level)
        self.evidence_level = evidence_level

    def process_security_event(
        self,
        threat_level: str = "HIGH",
        threat_type: str = "TAMPERING_SUSPECTED",
        state_machine: Optional[RecoveryStateMachine] = None,
        executed: bool = True,
    ) -> SecurityRecoveryResult:
        if not executed:
            rec = self.recommendation_engine.generate_recommendation(incident_severity="LOW")
            return SecurityRecoveryResult(
                threat_detected=False,
                recovery_state_entered=RecoveryState.NOT_EXECUTED,
                recommendation=rec,
                auto_execution_blocked=True,
                evidence_level=self.evidence_level,
                details={"message": "Not executed."},
            )

        # Transition recovery state machine if provided
        target_state = RecoveryState.RECOVERY_ANALYSIS
        if state_machine:
            if state_machine.current_state == RecoveryState.NORMAL:
                state_machine.transition_to(
                    RecoveryState.INCIDENT_DETECTED,
                    reason=f"Security event triggered: {threat_type}",
                )
            if state_machine.current_state == RecoveryState.INCIDENT_DETECTED:
                state_machine.transition_to(
                    RecoveryState.RECOVERY_ANALYSIS,
                    reason="Security threat analysis underway",
                )
            target_state = state_machine.current_state

        # Generate recommendation with strict auto_execution_blocked = True
        if threat_type == "CONTAINER_COMPROMISE":
            rec = self.recommendation_engine.generate_recommendation(
                incident_severity="HIGH",
                deployment_failed=True,
            )
        elif threat_type == "DATA_TAMPERING":
            rec = self.recommendation_engine.generate_recommendation(
                incident_severity="HIGH",
                database_failed=True,
            )
        else:
            rec = self.recommendation_engine.generate_recommendation(
                incident_severity="HIGH",
                tampering_detected=(threat_level == "CRITICAL"),
            )

        return SecurityRecoveryResult(
            threat_detected=True,
            recovery_state_entered=target_state,
            recommendation=rec,
            auto_execution_blocked=True,  # STRICT SAFETY RULE
            evidence_level=self.evidence_level,
            details={
                "threat_level": threat_level,
                "threat_type": threat_type,
            },
        )
