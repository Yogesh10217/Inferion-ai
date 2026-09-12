from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.deployment.models import (
    DeploymentIdentity,
    DeploymentState,
    PlatformReadinessClassification,
    RollbackEvidence,
    RollbackPlan,
    RollbackState,
    RollbackTrigger,
)


class RollbackStrategyEngine:
    """Generates structured rollback plans and manages deployment safety state.
    
    Produces ROLLBACK_STRATEGY_READY classification without executing actual runtime rollback.
    """

    TRIGGER_ACTION_MAP: Dict[RollbackTrigger, List[str]] = {
        RollbackTrigger.CONFIGURATION_FAILURE: [
            "Revert configuration changes to last validated commit",
            "Validate environment variable schema against production profile",
            "Audit secrets for placeholder or unsafe values",
        ],
        RollbackTrigger.READINESS_FAILURE: [
            "Inspect container readiness probes and dependency sockets",
            "Check network isolation and port bindings",
            "Verify database and cache connection pools",
        ],
        RollbackTrigger.HEALTH_REGRESSION: [
            "Analyze application health probe failure trace",
            "Divert incoming traffic to healthy cluster instances",
            "Trigger container diagnostic memory/thread dump",
        ],
        RollbackTrigger.DEPENDENCY_FAILURE: [
            "Probe external infrastructure dependency endpoints (DB, Redis)",
            "Verify network security groups and IAM credentials",
            "Initiate circuit breaker or fallback state if permitted",
        ],
        RollbackTrigger.CONTAINER_FAILURE: [
            "Inspect Docker container crash logs and exit status",
            "Verify non-root user permissions and file system mounts",
            "Roll back to previous immutable container image tag",
        ],
        RollbackTrigger.MANAGER_REGISTRATION_FAILURE: [
            "Inspect ServiceContainer manager graph initialization",
            "Verify all 9 platform intelligence managers registered cleanly",
            "Restart container with verbose lifecycle diagnostics",
        ],
        RollbackTrigger.SECURITY_POLICY_VIOLATION: [
            "Enforce strict HTTP security headers and CORS origin restrictions",
            "Disable exposed API documentation endpoints in PRODUCTION",
            "Audit authentication and authorization middleware chain",
        ],
        RollbackTrigger.SECRET_EXPOSURE_DETECTION: [
            "Immediately rotate leaked secret credentials",
            "Execute SHA-256 secret sanitizer audit across logs and diagnostics",
            "Block release until zero secret canary leakage is re-certified",
        ],
    }

    @classmethod
    def generate_rollback_plan(
        cls,
        trigger: RollbackTrigger,
        deployment_identity: DeploymentIdentity,
        previous_deployment_reference: Optional[str] = None,
        evidence_details: Optional[Dict[str, Any]] = None,
    ) -> RollbackPlan:
        evidence = RollbackEvidence(
            trigger=trigger,
            detected_at=datetime.now(timezone.utc).isoformat(),
            details=evidence_details or {},
        )

        prev_ref = (
            previous_deployment_reference
            if previous_deployment_reference and previous_deployment_reference.strip()
            else "NO_PREVIOUS_DEPLOYMENT_REFERENCE"
        )

        operator_actions = cls.TRIGGER_ACTION_MAP.get(
            trigger,
            ["Perform emergency platform audit", "Halt deployment rollout"],
        )

        auto_actions = [
            "Set DeploymentReleaseStatus to BLOCKED",
            "Set DeploymentDecision to ROLLBACK_REQUIRED",
            "Preserve deployment execution telemetry and diagnostic logs",
        ]

        validation_reqs = [
            "Run automated production safety test suite",
            "Verify zero secret canary leakage",
            "Confirm ServiceContainer 9-manager invariant",
        ]

        return RollbackPlan(
            trigger=trigger,
            deployment_identity=deployment_identity,
            previous_deployment_reference=prev_ref,
            required_operator_actions=operator_actions,
            automatic_actions=auto_actions,
            validation_requirements=validation_reqs,
            evidence=evidence,
            safety_classification=PlatformReadinessClassification.ROLLBACK_STRATEGY_READY,
        )

    @classmethod
    def initialize_rollback_state(
        cls,
        trigger: Optional[RollbackTrigger] = None,
        deployment_identity: Optional[DeploymentIdentity] = None,
        previous_reference: Optional[str] = None,
    ) -> RollbackState:
        if trigger and deployment_identity:
            plan = cls.generate_rollback_plan(
                trigger=trigger,
                deployment_identity=deployment_identity,
                previous_deployment_reference=previous_reference,
            )
            return RollbackState(
                status="ROLLBACK_STRATEGY_READY",
                active_plan=plan,
                executed=False,
            )

        return RollbackState(
            status="ROLLBACK_STRATEGY_READY",
            active_plan=None,
            executed=False,
        )
