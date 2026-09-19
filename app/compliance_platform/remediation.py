"""Compliance Remediation Planning & Delegation Subsystem."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.approvals.approval_engine import ApprovalEngine
from app.compliance_platform.exceptions import ComplianceRemediationException


class RemediationPriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class RemediationStatus(str, Enum):
    PROPOSED = "PROPOSED"
    RISK_EVALUATION = "RISK_EVALUATION"
    REQUIRES_APPROVAL = "REQUIRES_APPROVAL"
    APPROVED = "APPROVED"
    DELEGATED = "DELEGATED"
    EXECUTING = "EXECUTING"
    VERIFICATION = "VERIFICATION"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    COMPENSATED = "COMPENSATED"


class RemediationAction(BaseModel):
    action_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    target_subsystem: str  # e.g., OrchestrationManager, PlatformOperationsManager
    action_type: str
    description: str
    parameters: Dict[str, Any] = Field(default_factory=dict)


class ComplianceRemediationPlan(BaseModel):
    plan_id: str = Field(default_factory=lambda: f"rem_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    finding_id: str
    priority: RemediationPriority = RemediationPriority.HIGH
    status: RemediationStatus = RemediationStatus.PROPOSED
    actions: List[RemediationAction] = Field(default_factory=list)
    risk_level: str = "HIGH"
    approval_request_id: Optional[str] = None
    delegated_subsystem: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ComplianceRemediationManager:
    """Manages remediation plans, risk approvals, and delegation to existing platform managers."""

    def __init__(self, approval_engine: Optional[ApprovalEngine] = None) -> None:
        self.approval_engine = approval_engine or ApprovalEngine()
        self._plans: Dict[str, ComplianceRemediationPlan] = {}

    def create_remediation_plan(
        self,
        tenant_id: str,
        finding_id: str,
        actions: List[RemediationAction],
        priority: RemediationPriority = RemediationPriority.HIGH,
        risk_level: str = "HIGH",
        requested_by: str = "system",
    ) -> ComplianceRemediationPlan:
        plan = ComplianceRemediationPlan(
            tenant_id=tenant_id,
            finding_id=finding_id,
            priority=priority,
            actions=actions,
            risk_level=risk_level,
        )

        if risk_level in ("HIGH", "CRITICAL"):
            plan.status = RemediationStatus.REQUIRES_APPROVAL
            # Request approval from ApprovalEngine
            app_req = self.approval_engine.request_approval(
                execution_id=finding_id,
                action_type=f"COMPLIANCE_REMEDIATION_{priority.value}",
                requester=requested_by,
                tenant_id=tenant_id,
                payload={"finding_id": finding_id, "risk_level": risk_level},
            )
            plan.approval_request_id = app_req.request_id
        else:
            plan.status = RemediationStatus.APPROVED

        self._plans[plan.plan_id] = plan
        return plan

    def get_plan(self, plan_id: str, tenant_id: str) -> ComplianceRemediationPlan:
        plan = self._plans.get(plan_id)
        if not plan or plan.tenant_id != tenant_id:
            raise ComplianceRemediationException(f"Remediation plan '{plan_id}' not found for tenant '{tenant_id}'.")
        return plan

    def delegate_execution(
        self, plan_id: str, tenant_id: str, delegated_subsystem: str = "PlatformOperationsManager"
    ) -> ComplianceRemediationPlan:
        plan = self.get_plan(plan_id, tenant_id)
        if plan.status not in (RemediationStatus.APPROVED, RemediationStatus.PROPOSED):
            raise ComplianceRemediationException(
                f"Remediation plan '{plan_id}' is not in APPROVED state (Status: {plan.status})."
            )

        plan.status = RemediationStatus.DELEGATED
        plan.delegated_subsystem = delegated_subsystem
        plan.status = RemediationStatus.COMPLETED
        return plan
