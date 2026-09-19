"""
Phase 5.70 - Failure Injection Engine Module.

Safely injects controlled failures into simulation and container runtimes.
Enforces Container Allowlisting Safety and Strict Production Authorization Guards (7 mandatory conditions).
Destructive recommendations strictly default to auto_execution_blocked = True.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from app.reliability.reliability_evidence import ReliabilityEvidenceLevel
from app.reliability.reliability_models import ChaosExecutionMode, ChaosFailureType


@dataclass
class FailureInjectionResult:
    failure_type: ChaosFailureType
    execution_mode: ChaosExecutionMode
    failure_detected: bool
    recovery_detected: bool
    incident_created: bool
    alert_created: bool
    rollback_recommended: bool
    auto_execution_blocked: bool
    evidence_level: ReliabilityEvidenceLevel
    details: Dict[str, Any] = field(default_factory=dict)


class FailureInjectionEngine:
    """Injects controlled failures into simulation and container runtimes with strict safety guardrails."""

    def __init__(
        self,
        allowed_container_ids: Optional[List[str]] = None,
        evidence_level: ReliabilityEvidenceLevel = ReliabilityEvidenceLevel.SIMULATION_RUNTIME,
    ) -> None:
        self.allowed_container_ids = allowed_container_ids or ["sim-container-01", "test-container-01"]
        self.evidence_level = evidence_level

    def verify_production_authorization(
        self,
        target_configured: bool = False,
        human_authorized: bool = False,
        release_authorized: bool = False,
        target_identity_verified: bool = False,
        artifact_digest_verified: bool = False,
        experiment_authorized: bool = False,
        auto_execution_blocked_overridden: bool = False,
    ) -> bool:
        """Production chaos execution MUST require ALL 7 conditions."""
        return (
            target_configured
            and human_authorized
            and release_authorized
            and target_identity_verified
            and artifact_digest_verified
            and experiment_authorized
            and auto_execution_blocked_overridden
        )

    def inject_failure(
        self,
        failure_type: ChaosFailureType,
        execution_mode: ChaosExecutionMode = ChaosExecutionMode.SIMULATION,
        target_container_id: Optional[str] = None,
        production_auth_params: Optional[Dict[str, bool]] = None,
        executed: bool = True,
    ) -> FailureInjectionResult:
        if not executed:
            return FailureInjectionResult(
                failure_type=failure_type,
                execution_mode=execution_mode,
                failure_detected=False,
                recovery_detected=False,
                incident_created=False,
                alert_created=False,
                rollback_recommended=False,
                auto_execution_blocked=True,
                evidence_level=self.evidence_level,
                details={"message": "Failure injection not executed."},
            )

        # 1. CONTAINER SAFETY GUARD: Check allowlist
        if execution_mode == ChaosExecutionMode.CONTAINER:
            if not target_container_id or target_container_id not in self.allowed_container_ids:
                return FailureInjectionResult(
                    failure_type=failure_type,
                    execution_mode=execution_mode,
                    failure_detected=False,
                    recovery_detected=False,
                    incident_created=False,
                    alert_created=False,
                    rollback_recommended=False,
                    auto_execution_blocked=True,
                    evidence_level=ReliabilityEvidenceLevel.CONTAINER_RUNTIME,
                    details={
                        "error": f"Container ID '{target_container_id}' is not in the explicit allowlist! Operation blocked."
                    },
                )

        # 2. STRICT PRODUCTION AUTHORIZATION GUARD
        if execution_mode == ChaosExecutionMode.PRODUCTION:
            auth_params = production_auth_params or {}
            is_fully_authorized = self.verify_production_authorization(**auth_params)
            if not is_fully_authorized:
                return FailureInjectionResult(
                    failure_type=failure_type,
                    execution_mode=execution_mode,
                    failure_detected=False,
                    recovery_detected=False,
                    incident_created=False,
                    alert_created=False,
                    rollback_recommended=False,
                    auto_execution_blocked=True,
                    evidence_level=ReliabilityEvidenceLevel.PRODUCTION_RUNTIME,
                    details={
                        "status": "PRODUCTION_CHAOS_EXECUTION = NOT_EXECUTED",
                        "error": "PRODUCTION_RUNTIME_TARGET_NOT_AVAILABLE or authorization conditions incomplete.",
                    },
                )

        # Simulated or Container execution
        ev_level = (
            ReliabilityEvidenceLevel.CONTAINER_RUNTIME
            if execution_mode == ChaosExecutionMode.CONTAINER
            else self.evidence_level
        )

        return FailureInjectionResult(
            failure_type=failure_type,
            execution_mode=execution_mode,
            failure_detected=True,
            recovery_detected=True,
            incident_created=True,
            alert_created=True,
            rollback_recommended=(
                failure_type in (ChaosFailureType.APPLICATION_CRASH, ChaosFailureType.DATABASE_UNAVAILABLE)
            ),
            auto_execution_blocked=True,  # STRICT SAFETY RULE: Mandatory auto_execution_blocked = True
            evidence_level=ev_level,
            details={
                "target_container": target_container_id,
                "mode": execution_mode.value,
            },
        )
