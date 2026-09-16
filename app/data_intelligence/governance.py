"""Data intelligence governance engine (Phase 5.43)."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List

from pydantic import BaseModel, Field

from app.data_intelligence.exceptions import CrossTenantDataIntelligenceException


class DataGovernanceDecisionStatus(str, Enum):
    ALLOW = "ALLOW"
    DENY = "DENY"
    REQUIRE_APPROVAL = "REQUIRE_APPROVAL"
    RESTRICT = "RESTRICT"
    BLOCK = "BLOCK"


class DataGovernanceRequirement(BaseModel):
    requirement_id: str = Field(default_factory=lambda: f"dgov-req-{uuid.uuid4().hex[:8]}")
    code: str
    description: str
    satisfied: bool = True


class DataGovernanceDecision(BaseModel):
    decision_id: str = Field(default_factory=lambda: f"dgov-dec-{uuid.uuid4().hex[:12]}")
    tenant_id: str
    action_type: str
    dataset_id: str
    status: DataGovernanceDecisionStatus
    risk_score: float = 0.0
    reason: str
    requirements: List[DataGovernanceRequirement] = Field(default_factory=list)
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DataIntelligenceGovernanceEngine:
    """Orchestrates data governance evaluations across sensitivity, policy, risk, and approval engines."""

    def __init__(self) -> None:
        self._decisions: Dict[str, DataGovernanceDecision] = {}

    def evaluate_governance(
        self,
        tenant_id: str,
        dataset_id: str,
        action_type: str,
        sensitivity_tier: str = "CONFIDENTIAL",
        risk_score: float = 20.0,
        downstream_impact_count: int = 1,
        is_blocked: bool = False,
        requires_approval: bool = False,
    ) -> DataGovernanceDecision:
        reqs: List[DataGovernanceRequirement] = []

        # High-risk action checks
        high_risk_actions = {"dataset_rollback", "production_schema_migration", "large_scale_data_repair", "data_deletion", "sensitive_dataset_reprocessing"}
        if action_type.lower() in high_risk_actions or requires_approval or sensitivity_tier == "RESTRICTED":
            requires_approval = True

        if is_blocked:
            reqs.append(DataGovernanceRequirement(code="GOV_BLOCK", description="Data policy block enforced", satisfied=False))
            status = DataGovernanceDecisionStatus.BLOCK
            reason = f"Data action '{action_type}' blocked by policy."
        elif requires_approval or risk_score >= 75.0 or downstream_impact_count > 10:
            reqs.append(DataGovernanceRequirement(code="APPROVAL_REQUIRED", description="Human approval required for high-risk data action", satisfied=False))
            status = DataGovernanceDecisionStatus.REQUIRE_APPROVAL
            reason = f"High-risk data action '{action_type}' (risk: {risk_score:.1f}) requires explicit human approval."
        elif risk_score >= 50.0:
            status = DataGovernanceDecisionStatus.RESTRICT
            reason = f"Elevated risk score ({risk_score:.1f}) enforces RESTRICT constraints."
        elif risk_score >= 35.0:
            status = DataGovernanceDecisionStatus.DENY
            reason = f"Moderate risk score ({risk_score:.1f}) DENY status."
        else:
            status = DataGovernanceDecisionStatus.ALLOW
            reason = f"Data action '{action_type}' satisfies all governance constraints."

        dec = DataGovernanceDecision(
            tenant_id=tenant_id,
            action_type=action_type,
            dataset_id=dataset_id,
            status=status,
            risk_score=risk_score,
            reason=reason,
            requirements=reqs,
        )
        self._decisions[dec.decision_id] = dec
        return dec

    def get_decision(self, tenant_id: str, decision_id: str) -> DataGovernanceDecision:
        dec = self._decisions.get(decision_id)
        if not dec or dec.tenant_id != tenant_id:
            raise CrossTenantDataIntelligenceException()
        return dec
