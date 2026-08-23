"""Governance Remediation Orchestration Subsystem."""

from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.approvals.approval_engine import ApprovalEngine
from app.data_governance.exceptions import DataGovernanceException


class RemediationStatus(str, Enum):
    PROPOSED = "PROPOSED"
    APPROVAL_REQUIRED = "APPROVAL_REQUIRED"
    APPROVED = "APPROVED"
    DELEGATED = "DELEGATED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class RemediationAction(str, Enum):
    QUARANTINE_ASSET = "QUARANTINE_ASSET"
    ENFORCE_REDACTION = "ENFORCE_REDACTION"
    REVOKE_SHARING = "REVOKE_SHARING"
    TRIGGER_QUALITY_REMEDIATION = "TRIGGER_QUALITY_REMEDIATION"
    PURGE_NON_COMPLIANT_DATA = "PURGE_NON_COMPLIANT_DATA"
    RECLASSIFY_ASSET = "RECLASSIFY_ASSET"


class DataRemediationPlan(BaseModel):
    plan_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    asset_id: str
    action: RemediationAction
    status: RemediationStatus = RemediationStatus.PROPOSED
    is_high_risk: bool = True
    approval_request_id: Optional[str] = None
    target_subsystem: str = "PlatformOperationsManager"
    idempotency_key: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    executed_at: Optional[datetime] = None


class DataRemediationManager:
    """Orchestrates non-mutating remediation planning and delegates execution."""

    def __init__(self, approval_engine: Optional[ApprovalEngine] = None) -> None:
        self.approval_engine = approval_engine or ApprovalEngine()
        self._plans: Dict[str, DataRemediationPlan] = {}

    def propose_remediation_plan(
        self,
        tenant_id: str,
        asset_id: str,
        action: RemediationAction,
        is_high_risk: bool = True,
        target_subsystem: str = "PlatformOperationsManager",
        requester_id: str = "system",
    ) -> DataRemediationPlan:
        plan = DataRemediationPlan(
            tenant_id=tenant_id,
            asset_id=asset_id,
            action=action,
            is_high_risk=is_high_risk,
            target_subsystem=target_subsystem,
        )

        if is_high_risk:
            plan.status = RemediationStatus.APPROVAL_REQUIRED
            # Request approval from ApprovalEngine
            app_req = self.approval_engine.request_approval(
                execution_id=asset_id,
                action_type=f"REMEDIATION_{action.value}",
                requester=requester_id,
                tenant_id=tenant_id,
                payload={"plan_id": plan.plan_id, "target_subsystem": target_subsystem},
            )

            plan.approval_request_id = app_req.request_id

        self._plans[plan.plan_id] = plan
        return plan

    def delegate_execution(self, plan_id: str, tenant_id: str) -> DataRemediationPlan:
        plan = self._plans.get(plan_id)
        if not plan or plan.tenant_id != tenant_id:
            raise DataGovernanceException(f"Remediation plan '{plan_id}' not found.", tenant_id=tenant_id)

        if plan.is_high_risk and plan.status != RemediationStatus.APPROVED:
            raise DataGovernanceException(
                f"Remediation plan '{plan_id}' requires explicit approval before execution.",
                tenant_id=tenant_id,
            )

        plan.status = RemediationStatus.DELEGATED
        plan.executed_at = datetime.now(timezone.utc)
        plan.status = RemediationStatus.COMPLETED
        return plan

    def approve_remediation_plan(self, plan_id: str, approver_id: str) -> DataRemediationPlan:
        plan = self._plans.get(plan_id)
        if not plan:
            raise DataGovernanceException(f"Remediation plan '{plan_id}' not found.")
        plan.status = RemediationStatus.APPROVED
        return plan
