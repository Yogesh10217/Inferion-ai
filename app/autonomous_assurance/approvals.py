"""
Autonomous Approvals Subsystem.
Manages human approval routing, multi-stage approval, escalation, and timeout handling for workflows.
"""

import uuid
from datetime import datetime, timezone
from typing import Dict, Optional

from pydantic import BaseModel, Field

from app.autonomous_assurance.exceptions import (
    CrossTenantAutonomousAssuranceException,
    HighRiskAutonomousActionRequiresApprovalException,
)


class AutonomousApprovalRequirement(BaseModel):
    requirement_id: str = Field(default_factory=lambda: f"apprreq_{uuid.uuid4().hex[:12]}")
    workflow_id: str
    tenant_id: str
    approver_role: str = "SECURITY_ADMIN"
    stage: int = 1
    timeout_seconds: int = 86400
    is_approved: bool = False
    approved_by: Optional[str] = None
    comments: Optional[str] = None
    requested_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    approved_at: Optional[datetime] = None


class ApprovalRoutingEngine:
    """Manages approval context routing and verification."""

    def __init__(self) -> None:
        self._approvals: Dict[str, AutonomousApprovalRequirement] = {}

    def create_approval_request(self, workflow_id: str, tenant_id: str, approver_role: str = "SECURITY_ADMIN") -> AutonomousApprovalRequirement:
        req = AutonomousApprovalRequirement(workflow_id=workflow_id, tenant_id=tenant_id, approver_role=approver_role)
        self._approvals[workflow_id] = req
        return req

    def submit_approval(self, workflow_id: str, tenant_id: str, approved_by: str, approved: bool, comments: Optional[str] = None) -> AutonomousApprovalRequirement:
        req = self.get_approval(workflow_id, tenant_id)
        req.is_approved = approved
        req.approved_by = approved_by
        req.comments = comments
        req.approved_at = datetime.now(timezone.utc)
        return req

    def get_approval(self, workflow_id: str, tenant_id: str) -> AutonomousApprovalRequirement:
        req = self._approvals.get(workflow_id)
        if not req:
            req = self.create_approval_request(workflow_id, tenant_id)
        if req.tenant_id != tenant_id and tenant_id != "global":
            raise CrossTenantAutonomousAssuranceException(f"Unauthorized cross-tenant access to approval request for workflow '{workflow_id}'")
        return req

    def is_approved(self, workflow_id: str, tenant_id: str) -> bool:
        req = self._approvals.get(workflow_id)
        return req.is_approved if req else False

    def require_approval_check(self, workflow_id: str, tenant_id: str, risk_level: Optional[str] = None) -> None:
        if not self.is_approved(workflow_id, tenant_id):
            raise HighRiskAutonomousActionRequiresApprovalException(
                f"Workflow '{workflow_id}' requires human approval before delegation."
            )
