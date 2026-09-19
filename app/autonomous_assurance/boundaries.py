"""
Workflow Operational Safety Boundaries Subsystem (Addition #3).
Defines explicit execution safety boundaries: AUTONOMOUS_ALLOWED, APPROVAL_REQUIRED, ADVISORY_ONLY, and PROHIBITED.
"""

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from app.autonomous_assurance.exceptions import (
    HighRiskAutonomousActionRequiresApprovalException,
    WorkflowBoundaryViolationException,
)


class OperationalBoundaryMode(str, Enum):
    AUTONOMOUS_ALLOWED = "AUTONOMOUS_ALLOWED"
    APPROVAL_REQUIRED = "APPROVAL_REQUIRED"
    ADVISORY_ONLY = "ADVISORY_ONLY"
    PROHIBITED = "PROHIBITED"


BoundaryMode = OperationalBoundaryMode


class ActionCategory(str, Enum):
    GENERATE_RECOMMENDATION = "GENERATE_RECOMMENDATION"
    CREATE_INVESTIGATION = "CREATE_INVESTIGATION"
    RECORD_EVIDENCE = "RECORD_EVIDENCE"
    VERIFY_HEALTH = "VERIFY_HEALTH"
    RESTART_SERVICE = "RESTART_SERVICE"
    ROTATE_SECRET = "ROTATE_SECRET"  # nosec B105
    SCALE_INFRASTRUCTURE = "SCALE_INFRASTRUCTURE"
    DISABLE_IDENTITY = "DISABLE_IDENTITY"
    DEPLOY_APPLICATION = "DEPLOY_APPLICATION"
    ROLLBACK_DEPLOYMENT = "ROLLBACK_DEPLOYMENT"
    QUARANTINE_ENDPOINT = "QUARANTINE_ENDPOINT"
    DELETE_PRODUCTION_DATA = "DELETE_PRODUCTION_DATA"
    DISABLE_ADMIN_PRIVILEGE = "DISABLE_ADMIN_PRIVILEGE"
    OVERRIDE_TENANT_ISOLATION = "OVERRIDE_TENANT_ISOLATION"


# Pre-configured safety matrix for platform action categories
DEFAULT_SAFETY_BOUNDARIES: Dict[str, OperationalBoundaryMode] = {
    "GENERATE_RECOMMENDATION": OperationalBoundaryMode.AUTONOMOUS_ALLOWED,
    "CREATE_INVESTIGATION": OperationalBoundaryMode.AUTONOMOUS_ALLOWED,
    "RECORD_EVIDENCE": OperationalBoundaryMode.AUTONOMOUS_ALLOWED,
    "VERIFY_HEALTH": OperationalBoundaryMode.AUTONOMOUS_ALLOWED,
    "RESTART_SERVICE": OperationalBoundaryMode.APPROVAL_REQUIRED,
    "ROTATE_SECRET": OperationalBoundaryMode.APPROVAL_REQUIRED,
    "SCALE_INFRASTRUCTURE": OperationalBoundaryMode.APPROVAL_REQUIRED,
    "DISABLE_IDENTITY": OperationalBoundaryMode.APPROVAL_REQUIRED,
    "DEPLOY_APPLICATION": OperationalBoundaryMode.APPROVAL_REQUIRED,
    "ROLLBACK_DEPLOYMENT": OperationalBoundaryMode.APPROVAL_REQUIRED,
    "QUARANTINE_ENDPOINT": OperationalBoundaryMode.APPROVAL_REQUIRED,
    "DELETE_PRODUCTION_DATA": OperationalBoundaryMode.PROHIBITED,
    "DISABLE_ADMIN_PRIVILEGE": OperationalBoundaryMode.PROHIBITED,
    "OVERRIDE_TENANT_ISOLATION": OperationalBoundaryMode.PROHIBITED,
}


class EvaluationResult(BaseModel):
    mode: OperationalBoundaryMode


class WorkflowSafetyBoundaryEngine:
    """Evaluates requested actions against explicit platform safety boundaries."""

    def __init__(self, custom_boundaries: Optional[Dict[str, OperationalBoundaryMode]] = None) -> None:
        self.boundaries = dict(DEFAULT_SAFETY_BOUNDARIES)
        if custom_boundaries:
            self.boundaries.update(custom_boundaries)

    def evaluate_action(self, tenant_id: str, action_name: str) -> EvaluationResult:
        mode = self.boundaries.get(action_name.upper(), OperationalBoundaryMode.APPROVAL_REQUIRED)
        return EvaluationResult(mode=mode)

    def evaluate_action_boundary(
        self, action_name: str, workflow_id: str, is_approved: bool = False
    ) -> OperationalBoundaryMode:
        mode = self.boundaries.get(action_name.upper(), OperationalBoundaryMode.APPROVAL_REQUIRED)

        if mode == OperationalBoundaryMode.PROHIBITED:
            raise WorkflowBoundaryViolationException(
                f"Action '{action_name}' is PROHIBITED by platform safety boundaries for workflow '{workflow_id}'."
            )

        if mode == OperationalBoundaryMode.APPROVAL_REQUIRED and not is_approved:
            raise HighRiskAutonomousActionRequiresApprovalException(
                f"High-risk action '{action_name}' requires human approval before delegation for workflow '{workflow_id}'."
            )

        return mode

    def enforce_boundaries(self, workflow_id: str, tenant_id: str, steps: Optional[List[Any]] = None) -> None:
        # Evaluates default prohibited check
        self.evaluate_action_boundary("DELETE_PRODUCTION_DATA", workflow_id)
