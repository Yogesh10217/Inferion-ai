"""Compliance Governance & Risk Evaluation Orchestration."""

from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.governance_platform.policy_evaluation import UnifiedPolicyEvaluator
from app.governance_platform.risk import RiskManager
from app.approvals.approval_engine import ApprovalEngine


class ComplianceGovernanceDecisionType(str, Enum):
    ALLOW = "ALLOW"
    WARN = "WARN"
    REQUIRE_APPROVAL = "REQUIRE_APPROVAL"
    RESTRICT = "RESTRICT"
    BLOCK = "BLOCK"


class ComplianceRiskAssessment(BaseModel):
    assessment_id: str = Field(default_factory=lambda: f"comprisk_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    risk_score: float
    risk_level: str  # LOW, MEDIUM, HIGH, CRITICAL
    factors: List[str] = Field(default_factory=list)


class ComplianceGovernanceDecision(BaseModel):
    decision_id: str = Field(default_factory=lambda: f"compdec_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    decision: ComplianceGovernanceDecisionType
    requires_approval: bool = False
    approval_request_id: Optional[str] = None
    reason: str
    risk_assessment: ComplianceRiskAssessment
    decided_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ComplianceGovernanceEngine:
    """Orchestrates compliance policies, risk evaluation, and human approvals."""

    def __init__(
        self,
        policy_evaluator: Optional[UnifiedPolicyEvaluator] = None,
        risk_manager: Optional[RiskManager] = None,
        approval_engine: Optional[ApprovalEngine] = None,
    ) -> None:
        self.policy_evaluator = policy_evaluator or UnifiedPolicyEvaluator()
        self.risk_manager = risk_manager or RiskManager()
        self.approval_engine = approval_engine or ApprovalEngine()

    def evaluate_remediation_governance(
        self,
        tenant_id: str,
        finding_id: str,
        risk_level: str = "HIGH",
        requested_by: str = "system",
    ) -> ComplianceGovernanceDecision:
        requires_approval = risk_level in ("HIGH", "CRITICAL")
        approval_req_id = None

        if requires_approval:
            decision_type = ComplianceGovernanceDecisionType.REQUIRE_APPROVAL
            reason = f"Remediation for finding '{finding_id}' carries {risk_level} risk and requires explicit approval."
            app_req = self.approval_engine.request_approval(
                execution_id=finding_id,
                action_type="COMPLIANCE_REMEDIATION",
                requester=requested_by,
                tenant_id=tenant_id,
                payload={"finding_id": finding_id, "risk_level": risk_level},
            )
            approval_req_id = app_req.request_id
        else:
            decision_type = ComplianceGovernanceDecisionType.ALLOW
            reason = "Remediation approved."

        risk_assessment = ComplianceRiskAssessment(
            tenant_id=tenant_id,
            risk_score=85.0 if requires_approval else 25.0,
            risk_level=risk_level,
            factors=[f"Finding ID: {finding_id}", f"Remediation Risk: {risk_level}"],
        )

        return ComplianceGovernanceDecision(
            tenant_id=tenant_id,
            decision=decision_type,
            requires_approval=requires_approval,
            approval_request_id=approval_req_id,
            reason=reason,
            risk_assessment=risk_assessment,
        )
