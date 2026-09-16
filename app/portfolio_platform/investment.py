"""Investment Governance Subsystem."""

import hashlib
import json
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, Optional

from pydantic import BaseModel, Field

from app.approvals.approval_engine import ApprovalEngine
from app.portfolio_platform.exceptions import (
    CrossTenantPortfolioAccessException,
    ImmutableInvestmentDecisionException,
    InvestmentNotFoundException,
)


class InvestmentType(str, Enum):
    NEW_INITIATIVE = "NEW_INITIATIVE"
    CAPACITY_EXPANSION = "CAPACITY_EXPANSION"
    INFRASTRUCTURE = "INFRASTRUCTURE"
    MAINTENANCE = "MAINTENANCE"


class InvestmentStatus(str, Enum):
    DRAFT = "DRAFT"
    EVALUATING = "EVALUATING"
    RECOMMENDED = "RECOMMENDED"
    REQUIRES_APPROVAL = "REQUIRES_APPROVAL"
    APPROVED = "APPROVED"
    FUNDED = "FUNDED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"


class InvestmentRisk(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class InvestmentProposal(BaseModel):
    proposal_id: str = Field(default_factory=lambda: f"inv_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    initiative_id: str
    amount_usd: float
    investment_type: InvestmentType = InvestmentType.NEW_INITIATIVE
    risk_level: InvestmentRisk = InvestmentRisk.HIGH
    status: InvestmentStatus = InvestmentStatus.DRAFT
    approval_request_id: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class InvestmentDecision(BaseModel):
    decision_id: str = Field(default_factory=lambda: f"invdec_{uuid.uuid4().hex[:12]}")
    proposal_id: str
    tenant_id: str
    initiative_id: str
    status: InvestmentStatus
    approved_amount_usd: float
    decision_fingerprint: str
    is_finalized: bool = True
    decided_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class InvestmentManager:
    """Manages investment proposals, risk evaluations, approvals, and immutable decisions."""

    def __init__(self, approval_engine: Optional[ApprovalEngine] = None) -> None:
        self.approval_engine = approval_engine or ApprovalEngine()
        self._proposals: Dict[str, InvestmentProposal] = {}
        self._decisions: Dict[str, InvestmentDecision] = {}

    def propose_investment(
        self,
        tenant_id: str,
        initiative_id: str,
        amount_usd: float,
        risk_level: InvestmentRisk = InvestmentRisk.HIGH,
        investment_type: InvestmentType = InvestmentType.NEW_INITIATIVE,
        requested_by: str = "program_lead",
    ) -> InvestmentProposal:
        proposal = InvestmentProposal(
            tenant_id=tenant_id,
            initiative_id=initiative_id,
            amount_usd=amount_usd,
            risk_level=risk_level,
            investment_type=investment_type,
        )

        # Enforce ApprovalEngine requirement for HIGH and CRITICAL risk investments
        if risk_level in (InvestmentRisk.HIGH, InvestmentRisk.CRITICAL):
            proposal.status = InvestmentStatus.REQUIRES_APPROVAL
            app_req = self.approval_engine.request_approval(
                execution_id=initiative_id,
                action_type=f"INVESTMENT_APPROVAL_{risk_level.value}",
                requester=requested_by,
                tenant_id=tenant_id,
                payload={"initiative_id": initiative_id, "amount_usd": amount_usd, "risk_level": risk_level.value},
            )
            proposal.approval_request_id = app_req.request_id
        else:
            proposal.status = InvestmentStatus.APPROVED

        self._proposals[proposal.proposal_id] = proposal
        return proposal

    def finalize_decision(self, proposal_id: str, tenant_id: str) -> InvestmentDecision:
        proposal = self.get_proposal(proposal_id, tenant_id)
        if proposal.status not in (InvestmentStatus.APPROVED, InvestmentStatus.RECOMMENDED):
            raise ImmutableInvestmentDecisionException(decision_id=proposal_id, tenant_id=tenant_id)

        canonical_str = json.dumps(
            {
                "proposal_id": proposal.proposal_id,
                "tenant_id": tenant_id,
                "initiative_id": proposal.initiative_id,
                "amount": proposal.amount_usd,
                "risk": proposal.risk_level.value,
            },
            sort_keys=True,
        )
        fingerprint = hashlib.sha256(canonical_str.encode("utf-8")).hexdigest()

        decision = InvestmentDecision(
            proposal_id=proposal.proposal_id,
            tenant_id=tenant_id,
            initiative_id=proposal.initiative_id,
            status=InvestmentStatus.APPROVED,
            approved_amount_usd=proposal.amount_usd,
            decision_fingerprint=fingerprint,
            is_finalized=True,
        )
        self._decisions[decision.decision_id] = decision
        proposal.status = InvestmentStatus.FUNDED
        return decision

    def get_proposal(self, proposal_id: str, tenant_id: str) -> InvestmentProposal:
        p = self._proposals.get(proposal_id)
        if not p:
            raise InvestmentNotFoundException(investment_id=proposal_id, tenant_id=tenant_id)
        if p.tenant_id != tenant_id and tenant_id != "global":
            raise CrossTenantPortfolioAccessException(request_tenant=tenant_id, target_tenant=p.tenant_id, resource_id=proposal_id)
        return p

    def get_decision(self, decision_id: str, tenant_id: str) -> InvestmentDecision:
        d = self._decisions.get(decision_id)
        if not d:
            raise InvestmentNotFoundException(investment_id=decision_id, tenant_id=tenant_id)
        if d.tenant_id != tenant_id and tenant_id != "global":
            raise CrossTenantPortfolioAccessException(request_tenant=tenant_id, target_tenant=d.tenant_id, resource_id=decision_id)
        return d
