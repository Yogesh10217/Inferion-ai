"""Integration Governance Engine (Phase 5.40)."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.integration_intelligence.exceptions import CrossTenantIntegrationAccessException


class IntegrationGovernanceStatus(str, Enum):
    ALLOW = "ALLOW"
    WARN = "WARN"
    REQUIRE_APPROVAL = "REQUIRE_APPROVAL"
    RESTRICT = "RESTRICT"
    BLOCK = "BLOCK"


class IntegrationGovernanceRequirement(BaseModel):
    requirement_id: str = Field(default_factory=lambda: f"req_{uuid.uuid4().hex[:8]}")
    code: str
    description: str
    is_hard_policy: bool = False
    satisfied: bool = True


class IntegrationGovernanceDecision(BaseModel):
    decision_id: str = Field(default_factory=lambda: f"gov_dec_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    workflow_id: str
    action_type: str
    status: IntegrationGovernanceStatus
    risk_score: float = 0.0
    hard_policy_violated: bool = False
    reason: str
    requirements: List[IntegrationGovernanceRequirement] = Field(default_factory=list)
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class IntegrationGovernanceEngine:
    """Orchestrates integration governance across policy, risk, and approval engines."""

    def __init__(self) -> None:
        self._decisions: Dict[str, IntegrationGovernanceDecision] = {}

    def evaluate_governance(
        self,
        tenant_id: str,
        workflow_id: str,
        action_type: str,
        risk_score: float = 15.0,
        hard_policy_violated: bool = False,
        requires_approval: bool = False,
        is_blocked: bool = False,
        context: Optional[Dict[str, Any]] = None,
    ) -> IntegrationGovernanceDecision:
        context = context or {}
        reqs: List[IntegrationGovernanceRequirement] = []

        if hard_policy_violated or is_blocked:
            reqs.append(IntegrationGovernanceRequirement(code="HARD_POL_INT", description="Hard policy violation", is_hard_policy=True, satisfied=False))
            status = IntegrationGovernanceStatus.BLOCK
            reason = "Hard policy violation or explicit block policy triggered BLOCK status."
        elif requires_approval or risk_score >= 80.0:
            reqs.append(IntegrationGovernanceRequirement(code="HUMAN_APPR_INT", description="Human approval for high-risk action", satisfied=False))
            status = IntegrationGovernanceStatus.REQUIRE_APPROVAL
            reason = f"High risk score ({risk_score}) or approval flag triggered REQUIRE_APPROVAL."
        elif risk_score >= 60.0:
            status = IntegrationGovernanceStatus.RESTRICT
            reason = f"Elevated risk score ({risk_score}) enforces RESTRICT constraints."
        elif risk_score >= 40.0:
            status = IntegrationGovernanceStatus.WARN
            reason = f"Moderate risk score ({risk_score}) issues WARN status."
        else:
            status = IntegrationGovernanceStatus.ALLOW
            reason = "Integration action satisfies all governance constraints."

        dec = IntegrationGovernanceDecision(
            tenant_id=tenant_id,
            workflow_id=workflow_id,
            action_type=action_type,
            status=status,
            risk_score=risk_score,
            hard_policy_violated=hard_policy_violated,
            reason=reason,
            requirements=reqs,
        )
        self._decisions[dec.decision_id] = dec
        return dec

    def get_decision(self, tenant_id: str, decision_id: str) -> IntegrationGovernanceDecision:
        dec = self._decisions.get(decision_id)
        if not dec or dec.tenant_id != tenant_id:
            raise CrossTenantIntegrationAccessException()
        return dec
