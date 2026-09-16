"""High-Level Data Governance Decision & Risk Assessment Subsystem."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field

from app.approvals.approval_engine import ApprovalEngine
from app.governance_platform.policy_evaluation import UnifiedPolicyEvaluator
from app.governance_platform.risk import RiskManager


class DataGovernanceDecisionType(str, Enum):
    ALLOW = "ALLOW"
    WARN = "WARN"
    MASK = "MASK"
    REDACT = "REDACT"
    REQUIRE_APPROVAL = "REQUIRE_APPROVAL"
    RESTRICT = "RESTRICT"
    QUARANTINE = "QUARANTINE"
    BLOCK = "BLOCK"


class DataRiskAssessment(BaseModel):
    assessment_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    asset_id: str
    risk_score: float  # 0.0 - 100.0
    risk_level: str  # LOW, MEDIUM, HIGH, CRITICAL
    factors: List[str] = Field(default_factory=list)
    assessed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DataGovernanceDecision(BaseModel):
    decision_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    asset_id: str
    action: DataGovernanceDecisionType
    risk_assessment: DataRiskAssessment
    reason: str
    decided_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DataGovernanceEngine:
    """Orchestrates high-level governance rules, risk assessments, and approval integrations."""

    def __init__(
        self,
        policy_evaluator: Optional[UnifiedPolicyEvaluator] = None,
        risk_manager: Optional[RiskManager] = None,
        approval_engine: Optional[ApprovalEngine] = None,
    ) -> None:
        self.policy_evaluator = policy_evaluator or UnifiedPolicyEvaluator()
        self.risk_manager = risk_manager or RiskManager()
        self.approval_engine = approval_engine or ApprovalEngine()

    def assess_asset_risk(
        self,
        tenant_id: str,
        asset_id: str,
        classification: str,
        trust_score: float,
        is_shared_externally: bool = False,
    ) -> DataRiskAssessment:
        factors = []
        base_risk = 20.0

        if classification == "HIGHLY_RESTRICTED":
            base_risk += 40.0
            factors.append("Classification is HIGHLY_RESTRICTED")
        elif classification == "RESTRICTED":
            base_risk += 25.0
            factors.append("Classification is RESTRICTED")

        if trust_score < 60.0:
            base_risk += 30.0
            factors.append(f"Low trust score: {trust_score:.1f}")

        if is_shared_externally:
            base_risk += 20.0
            factors.append("Asset is shared externally or cross-tenant")

        final_risk = min(100.0, base_risk)

        if final_risk >= 80.0:
            level = "CRITICAL"
        elif final_risk >= 60.0:
            level = "HIGH"
        elif final_risk >= 40.0:
            level = "MEDIUM"
        else:
            level = "LOW"

        return DataRiskAssessment(
            tenant_id=tenant_id,
            asset_id=asset_id,
            risk_score=final_risk,
            risk_level=level,
            factors=factors,
        )

    def evaluate_governance(
        self,
        tenant_id: str,
        asset_id: str,
        classification: str,
        trust_score: float,
        is_shared_externally: bool = False,
    ) -> DataGovernanceDecision:
        risk_assessment = self.assess_asset_risk(
            tenant_id=tenant_id,
            asset_id=asset_id,
            classification=classification,
            trust_score=trust_score,
            is_shared_externally=is_shared_externally,
        )

        if risk_assessment.risk_level == "CRITICAL":
            decision = DataGovernanceDecisionType.BLOCK
            reason = "Governance evaluation blocked request due to CRITICAL risk level."
        elif risk_assessment.risk_level == "HIGH":
            decision = DataGovernanceDecisionType.REQUIRE_APPROVAL
            reason = "High risk level requires human approval."
        elif classification == "RESTRICTED":
            decision = DataGovernanceDecisionType.MASK
            reason = "Restricted asset requires masking."
        else:
            decision = DataGovernanceDecisionType.ALLOW
            reason = "Asset governed and approved."

        return DataGovernanceDecision(
            tenant_id=tenant_id,
            asset_id=asset_id,
            action=decision,
            risk_assessment=risk_assessment,
            reason=reason,
        )
