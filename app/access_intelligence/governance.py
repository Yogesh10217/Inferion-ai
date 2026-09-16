"""Access Governance Orchestration Engine (Phase 5.39)."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.access_intelligence.exceptions import CrossTenantAccessIntelligenceException


class AccessGovernanceStatus(str, Enum):
    ALLOW = "ALLOW"
    WARN = "WARN"
    REQUIRE_APPROVAL = "REQUIRE_APPROVAL"
    RESTRICT = "RESTRICT"
    BLOCK = "BLOCK"


class AccessGovernanceRequirement(BaseModel):
    """Requirement associated with governance evaluation."""
    requirement_id: str = Field(default_factory=lambda: f"gov_req_{uuid.uuid4().hex[:8]}")
    code: str
    description: str
    is_hard_policy: bool = False
    satisfied: bool = True


class AccessGovernanceDecision(BaseModel):
    """Access Governance Evaluation Decision."""
    decision_id: str = Field(default_factory=lambda: f"gov_dec_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    subject_identity_id: str
    target_action: str
    status: AccessGovernanceStatus
    aggregate_risk_score: float = 0.0
    hard_policy_violated: bool = False
    reason: str
    requirements: List[AccessGovernanceRequirement] = Field(default_factory=list)
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AccessGovernanceEngine:
    """Orchestrates access governance across policy, risk, and approval engines."""

    def __init__(self) -> None:
        self._decisions: Dict[str, AccessGovernanceDecision] = {}

    def evaluate_governance(
        self,
        tenant_id: str,
        subject_identity_id: str,
        target_action: str,
        risk_score: float = 20.0,
        hard_policy_violation: bool = False,
        requires_human_approval: bool = False,
        context: Optional[Dict[str, Any]] = None,
    ) -> AccessGovernanceDecision:
        context = context or {}
        reqs: List[AccessGovernanceRequirement] = []

        if hard_policy_violation:
            reqs.append(AccessGovernanceRequirement(code="HARD_POL_01", description="Hard policy compliance rule", is_hard_policy=True, satisfied=False))
            status = AccessGovernanceStatus.BLOCK
            reason = "Hard policy violation overrides evaluation. Action is BLOCKED."
        elif requires_human_approval or risk_score >= 80.0:
            reqs.append(AccessGovernanceRequirement(code="HUMAN_APPR_01", description="Human approval for high-risk action", is_hard_policy=False, satisfied=False))
            status = AccessGovernanceStatus.REQUIRE_APPROVAL
            reason = f"High risk score ({risk_score}) or approval requirement triggered REQUIRE_APPROVAL."
        elif risk_score >= 60.0:
            status = AccessGovernanceStatus.RESTRICT
            reason = f"Elevated risk score ({risk_score}) enforces RESTRICT constraints."
        elif risk_score >= 40.0:
            status = AccessGovernanceStatus.WARN
            reason = f"Moderate risk score ({risk_score}) issues WARN status."
        else:
            status = AccessGovernanceStatus.ALLOW
            reason = "Access request satisfies all governance constraints."

        dec = AccessGovernanceDecision(
            tenant_id=tenant_id,
            subject_identity_id=subject_identity_id,
            target_action=target_action,
            status=status,
            aggregate_risk_score=risk_score,
            hard_policy_violated=hard_policy_violation,
            reason=reason,
            requirements=reqs,
        )
        self._decisions[dec.decision_id] = dec
        return dec

    def get_decision(self, tenant_id: str, decision_id: str) -> AccessGovernanceDecision:
        dec = self._decisions.get(decision_id)
        if not dec or dec.tenant_id != tenant_id:
            raise CrossTenantAccessIntelligenceException()
        return dec
