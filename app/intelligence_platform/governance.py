"""Intelligence Governance & Risk Evaluation Engine."""

from datetime import datetime, timezone
from enum import Enum
import uuid
import logging
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field

from app.governance_platform.policy_evaluation import UnifiedPolicyEvaluator, GovernanceDecision
from app.governance_platform.risk import RiskManager, RiskLevel
from app.intelligence_platform.exceptions import DecisionPolicyViolationException

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class IntelligencePolicyDecision(str, Enum):
    ALLOW = "ALLOW"
    WARN = "WARN"
    REQUIRE_APPROVAL = "REQUIRE_APPROVAL"
    RESTRICT = "RESTRICT"
    DEFER = "DEFER"
    BLOCK = "BLOCK"


class DecisionRiskAssessment(BaseModel):
    assessment_id: str = Field(default_factory=lambda: f"risk_{uuid.uuid4().hex[:10]}")
    risk_level: RiskLevel = RiskLevel.LOW
    risk_score: float = 0.15
    risk_factors: List[str] = Field(default_factory=list)
    requires_approval: bool = False


class IntelligenceGovernanceEngine:
    """Evaluates proposed intelligence decisions against platform governance policies and risk thresholds."""

    def __init__(
        self,
        policy_evaluator: Optional[UnifiedPolicyEvaluator] = None,
        risk_manager: Optional[RiskManager] = None,
    ) -> None:
        self.policy_evaluator = policy_evaluator or UnifiedPolicyEvaluator()
        self.risk_manager = risk_manager or RiskManager()

    def evaluate_decision(
        self,
        tenant_id: str,
        action_type: str,
        target_resource_id: str,
        risk_level_str: str = "LOW",
        trust_score: float = 85.0,
    ) -> tuple[IntelligencePolicyDecision, DecisionRiskAssessment]:
        # Determine risk
        r_level = RiskLevel.LOW
        if risk_level_str.upper() == "CRITICAL":
            r_level = RiskLevel.CRITICAL
        elif risk_level_str.upper() == "HIGH":
            r_level = RiskLevel.HIGH
        elif risk_level_str.upper() == "MEDIUM":
            r_level = RiskLevel.MEDIUM

        req_approval = r_level in (RiskLevel.HIGH, RiskLevel.CRITICAL) or trust_score < 70.0

        risk_assessment = DecisionRiskAssessment(
            risk_level=r_level,
            risk_score=0.85 if r_level in (RiskLevel.HIGH, RiskLevel.CRITICAL) else 0.20,
            risk_factors=[f"Action '{action_type}' on '{target_resource_id}' with risk {r_level.value}"],
            requires_approval=req_approval,
        )

        if r_level == RiskLevel.CRITICAL and trust_score < 50.0:
            dec = IntelligencePolicyDecision.BLOCK
        elif req_approval:
            dec = IntelligencePolicyDecision.REQUIRE_APPROVAL
        else:
            dec = IntelligencePolicyDecision.ALLOW

        logger.info(f"[INTELLIGENCE GOVERNANCE] Evaluated decision '{action_type}' for tenant '{tenant_id}': Decision={dec.value}, Risk={r_level.value}")
        return dec, risk_assessment
