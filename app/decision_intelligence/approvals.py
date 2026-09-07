"""
Decision Approvals Subsystem.
Manages human-in-the-loop approvals for high-risk decisions.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.decision_intelligence.exceptions import (
    HighRiskDecisionRequiresApprovalException,
    DecisionNotFoundException,
    CrossTenantDecisionIntelligenceException,
)


class DecisionApprovalRecord(BaseModel):
    approval_id: str = Field(default_factory=lambda: f"appr_{uuid.uuid4().hex[:12]}")
    decision_id: str
    tenant_id: str
    approver: str
    approved: bool
    comments: Optional[str] = None
    approved_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DecisionApprovalManager:
    """Manages approvals for decisions requiring human intervention."""

    def __init__(self) -> None:
        self._approvals: Dict[str, DecisionApprovalRecord] = {}

    def submit_approval(self, decision_id: str, tenant_id: str, approver: str, approved: bool, comments: Optional[str] = None) -> DecisionApprovalRecord:
        record = DecisionApprovalRecord(
            decision_id=decision_id,
            tenant_id=tenant_id,
            approver=approver,
            approved=approved,
            comments=comments,
        )
        self._approvals[decision_id] = record
        return record

    def is_approved(self, decision_id: str, tenant_id: str) -> bool:
        record = self._approvals.get(decision_id)
        if not record:
            return False
        if record.tenant_id != tenant_id and tenant_id != "global":
            raise CrossTenantDecisionIntelligenceException(f"Unauthorized cross-tenant access to approval for decision '{decision_id}'")
        return record.approved

    def require_approval_check(self, decision_id: str, tenant_id: str, risk_level: str) -> None:
        if risk_level in ["HIGH", "CRITICAL"] and not self.is_approved(decision_id, tenant_id):
            raise HighRiskDecisionRequiresApprovalException(
                f"High-risk decision '{decision_id}' (level '{risk_level}') requires human approval before delegation."
            )
