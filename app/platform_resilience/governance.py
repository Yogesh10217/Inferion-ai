"""Resilience Governance Engine Subsystem (Phase 5.37)."""

from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.platform_contracts.tenant import TenantAccessGuard
from app.platform_contracts.governance import GovernanceDecisionStatus
from app.governance import ResourceGovernanceEngine
from app.approvals import ApprovalEngine
from app.platform_resilience.exceptions import (
    ResiliencePolicyViolationException,
    HighRiskRecoveryRequiresApprovalException,
)


class ResilienceGovernanceDecision(BaseModel):
    decision_id: str = Field(default_factory=lambda: f"resgov_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    action_name: str
    status: GovernanceDecisionStatus = GovernanceDecisionStatus.ALLOW
    requires_approval: bool = False
    reasons: List[str] = Field(default_factory=list)
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ResilienceGovernanceEngine:
    """Resilience Governance Engine enforcing policies on destructive/high-risk resilience actions."""

    HIGH_RISK_KEYWORDS = ["FAILOVER", "RECOVER", "RESTORE", "SHED", "DISABLE", "CHAOS", "EXPERIMENT", "CORRUPT"]

    def __init__(
        self,
        approval_engine: Optional[ApprovalEngine] = None,
        tenant_guard: Optional[TenantAccessGuard] = None,
    ) -> None:
        self.approval_engine = approval_engine or ApprovalEngine()
        self.tenant_guard = tenant_guard or TenantAccessGuard()

    def evaluate_action_governance(
        self,
        tenant_id: str,
        action_name: str,
        resource_id: str,
        is_high_risk: bool = False,
    ) -> ResilienceGovernanceDecision:
        status = GovernanceDecisionStatus.ALLOW
        req_approval = False
        reasons = []

        is_kw_match = any(kw in action_name.upper() for kw in self.HIGH_RISK_KEYWORDS)

        if is_high_risk or is_kw_match:
            status = GovernanceDecisionStatus.REQUIRE_APPROVAL
            req_approval = True
            reasons.append(f"Resilience action '{action_name}' is high-risk. Human approval required.")

        return ResilienceGovernanceDecision(
            tenant_id=tenant_id,
            action_name=action_name,
            status=status,
            requires_approval=req_approval,
            reasons=reasons,
        )
