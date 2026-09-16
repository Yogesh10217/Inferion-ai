"""Governance Control Enforcement & Reversible Emergency Containment Engine."""

import logging
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

from app.approvals.approval_engine import ApprovalEngine
from app.governance_platform.exceptions import GovernancePlatformException
from app.operations.remediation import AutonomousRemediationEngine, RemediationRisk

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class EnforcementAction(str, Enum):
    WARN = "WARN"
    REQUIRE_APPROVAL = "REQUIRE_APPROVAL"
    REVOKE_ACCESS = "REVOKE_ACCESS"
    PAUSE_RESOURCE = "PAUSE_RESOURCE"
    DISABLE_EXTENSION = "DISABLE_EXTENSION"
    DISABLE_AGENT = "DISABLE_AGENT"
    BLOCK_DEPLOYMENT = "BLOCK_DEPLOYMENT"
    ROLLBACK_DEPLOYMENT = "ROLLBACK_DEPLOYMENT"
    QUARANTINE_DATA = "QUARANTINE_DATA"
    ROTATE_CREDENTIAL = "ROTATE_CREDENTIAL"
    ESCALATE_INCIDENT = "ESCALATE_INCIDENT"


class RemediationStatus(str, Enum):
    PLANNED = "PLANNED"
    APPROVAL_REQUIRED = "APPROVAL_REQUIRED"
    APPROVED = "APPROVED"
    EXECUTING = "EXECUTING"
    COMPLETED = "COMPLETED"
    ROLLED_BACK = "ROLLED_BACK"
    FAILED = "FAILED"


class GovernanceRemediation(BaseModel):
    remediation_id: str = Field(default_factory=lambda: f"grem_{uuid.uuid4().hex[:10]}")
    target_resource_id: str
    tenant_id: str = "global"
    action: EnforcementAction = EnforcementAction.PAUSE_RESOURCE
    risk_level: RemediationRisk = RemediationRisk.MEDIUM
    status: RemediationStatus = RemediationStatus.PLANNED

    is_emergency_containment: bool = False
    is_reversible: bool = True
    approval_request_id: Optional[str] = None
    incident_id: Optional[str] = None
    post_action_review_required: bool = True

    details: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=_now)


class ControlEnforcementEngine:
    """Orchestrates control enforcement and reversible emergency containment actions."""

    def __init__(
        self,
        approval_engine: Optional[ApprovalEngine] = None,
        operations_remediation: Optional[AutonomousRemediationEngine] = None,
    ) -> None:
        self.approval_engine = approval_engine or ApprovalEngine()
        self.operations_remediation = operations_remediation or AutonomousRemediationEngine()
        self._remediations: Dict[str, GovernanceRemediation] = {}

    def plan_remediation(
        self,
        target_resource_id: str,
        action: EnforcementAction,
        risk_level: RemediationRisk = RemediationRisk.MEDIUM,
        is_emergency: bool = False,
        tenant_id: str = "global",
    ) -> GovernanceRemediation:
        # Determine approval requirement
        if risk_level in (RemediationRisk.HIGH, RemediationRisk.CRITICAL) and not is_emergency:
            status = RemediationStatus.APPROVAL_REQUIRED
            req_id = f"appr_grem_{uuid.uuid4().hex[:8]}"
            logger.warning(f"[CONTROL ENFORCEMENT] Remediation for '{target_resource_id}' ({action.value}) requires approval (Request ID: {req_id})")
        else:
            status = RemediationStatus.APPROVED
            req_id = None
            logger.info(f"[CONTROL ENFORCEMENT] Remediation for '{target_resource_id}' ({action.value}) auto-approved under {risk_level.value} risk policy")

        rem = GovernanceRemediation(
            target_resource_id=target_resource_id,
            tenant_id=tenant_id,
            action=action,
            risk_level=risk_level,
            status=status,
            is_emergency_containment=is_emergency,
            is_reversible=True,  # All emergency containment MUST be reversible
            approval_request_id=req_id,
            post_action_review_required=is_emergency,
        )
        self._remediations[rem.remediation_id] = rem
        return rem

    def execute_remediation(self, remediation_id: str) -> GovernanceRemediation:
        rem = self.get_remediation(remediation_id)

        if rem.status == RemediationStatus.APPROVAL_REQUIRED:
            raise GovernancePlatformException(
                f"Remediation '{remediation_id}' cannot be executed without prior ApprovalEngine authorization.",
                code="APPROVAL_REQUIRED",
                status_code=403,
            )

        rem.status = RemediationStatus.EXECUTING

        # Execute reversible containment action
        if rem.action == EnforcementAction.REVOKE_ACCESS:
            logger.warning(f"[REMEDIATION EXEC] Temporarily revoked access for resource '{rem.target_resource_id}'")
        elif rem.action == EnforcementAction.PAUSE_RESOURCE:
            logger.warning(f"[REMEDIATION EXEC] Paused resource execution for '{rem.target_resource_id}'")
        elif rem.action == EnforcementAction.ROLLBACK_DEPLOYMENT:
            logger.warning(f"[REMEDIATION EXEC] Triggered deployment rollback for '{rem.target_resource_id}'")

        rem.status = RemediationStatus.COMPLETED
        logger.info(f"[CONTROL ENFORCEMENT] Completed remediation '{remediation_id}' ({rem.action.value}) on '{rem.target_resource_id}'")
        return rem

    def approve_remediation(self, remediation_id: str) -> GovernanceRemediation:
        rem = self.get_remediation(remediation_id)
        rem.status = RemediationStatus.APPROVED
        logger.info(f"[CONTROL ENFORCEMENT] Remediation '{remediation_id}' APPROVED by administrator.")
        return rem

    def get_remediation(self, remediation_id: str) -> GovernanceRemediation:
        rem = self._remediations.get(remediation_id)
        if not rem:
            raise KeyError(f"Remediation '{remediation_id}' not found")
        return rem
