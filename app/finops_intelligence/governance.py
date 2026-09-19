"""FinOps Governance Engine (Phase 5.42)."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List

from pydantic import BaseModel, Field

from app.finops_intelligence.exceptions import CrossTenantFinOpsIntelligenceException


class FinOpsGovernanceStatus(str, Enum):
    ALLOW = "ALLOW"
    DENY = "DENY"
    REQUIRE_APPROVAL = "REQUIRE_APPROVAL"
    RESTRICT = "RESTRICT"
    BLOCK = "BLOCK"


class FinOpsGovernanceRequirement(BaseModel):
    requirement_id: str = Field(default_factory=lambda: f"req_fin_{uuid.uuid4().hex[:8]}")
    code: str
    description: str
    satisfied: bool = True


class FinOpsGovernanceDecision(BaseModel):
    decision_id: str = Field(default_factory=lambda: f"gov_fin_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    action_type: str
    status: FinOpsGovernanceStatus
    risk_score: float = 0.0
    reason: str
    requirements: List[FinOpsGovernanceRequirement] = Field(default_factory=list)
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class FinOpsGovernanceEngine:
    """Orchestrates financial governance evaluations across policy, risk, and approval requirements."""

    def __init__(self) -> None:
        self._decisions: Dict[str, FinOpsGovernanceDecision] = {}

    def evaluate_governance(
        self,
        tenant_id: str,
        action_type: str,
        risk_score: float = 15.0,
        requires_approval: bool = False,
        is_blocked: bool = False,
    ) -> FinOpsGovernanceDecision:
        reqs: List[FinOpsGovernanceRequirement] = []

        if is_blocked:
            reqs.append(
                FinOpsGovernanceRequirement(code="POLICY_BLOCK", description="Financial policy block", satisfied=False)
            )
            status = FinOpsGovernanceStatus.BLOCK
            reason = f"Financial action '{action_type}' blocked by policy."
        elif requires_approval or risk_score >= 80.0:
            reqs.append(
                FinOpsGovernanceRequirement(
                    code="APPROVAL_REQ", description="Human approval required for financial action", satisfied=False
                )
            )
            status = FinOpsGovernanceStatus.REQUIRE_APPROVAL
            reason = (
                f"High-risk financial action '{action_type}' (risk: {risk_score}) requires explicit human approval."
            )
        elif risk_score >= 60.0:
            status = FinOpsGovernanceStatus.RESTRICT
            reason = f"Elevated risk score ({risk_score}) enforces RESTRICT constraints."
        elif risk_score >= 40.0:
            status = FinOpsGovernanceStatus.DENY
            reason = f"Moderate risk score ({risk_score}) DENY status."
        else:
            status = FinOpsGovernanceStatus.ALLOW
            reason = f"Financial action '{action_type}' satisfies all governance constraints."

        dec = FinOpsGovernanceDecision(
            tenant_id=tenant_id,
            action_type=action_type,
            status=status,
            risk_score=risk_score,
            reason=reason,
            requirements=reqs,
        )
        self._decisions[dec.decision_id] = dec
        return dec

    def get_decision(self, tenant_id: str, decision_id: str) -> FinOpsGovernanceDecision:
        dec = self._decisions.get(decision_id)
        if not dec or dec.tenant_id != tenant_id:
            raise CrossTenantFinOpsIntelligenceException()
        return dec
