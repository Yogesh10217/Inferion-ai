"""Developer Platform Governance & Pre-Deployment Policy Subsystem."""

from datetime import datetime, timezone
from enum import Enum
import uuid
import logging
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

from app.governance_platform.policy_evaluation import UnifiedPolicyEvaluator
from app.governance_platform.risk import RiskManager
from app.approvals.approval_engine import ApprovalEngine

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class DeveloperDecisionType(str, Enum):
    ALLOW = "ALLOW"
    WARN = "WARN"
    REQUIRE_APPROVAL = "REQUIRE_APPROVAL"
    RESTRICT = "RESTRICT"
    BLOCK = "BLOCK"


class DeveloperAccessDecision(BaseModel):
    decision_id: str = Field(default_factory=lambda: f"ddec_{uuid.uuid4().hex[:10]}")
    action: str
    tenant_id: str = "global"
    decision: DeveloperDecisionType = DeveloperDecisionType.ALLOW
    approval_request_id: Optional[str] = None
    reason: str = "Policy evaluated successfully"
    evaluated_at: datetime = Field(default_factory=_now)


class DeveloperGovernanceEngine:
    """Evaluates software delivery risk and enforces policy governance before deployments."""

    def __init__(
        self,
        policy_evaluator: Optional[UnifiedPolicyEvaluator] = None,
        risk_manager: Optional[RiskManager] = None,
        approval_engine: Optional[ApprovalEngine] = None,
    ) -> None:
        self.policy_evaluator = policy_evaluator or UnifiedPolicyEvaluator()
        self.risk_manager = risk_manager or RiskManager()
        self.approval_engine = approval_engine or ApprovalEngine()

    def evaluate_release_governance(self, project_id: str, action: str, risk_level: str = "LOW", tenant_id: str = "global") -> DeveloperAccessDecision:
        if risk_level in ("HIGH", "CRITICAL"):
            appr = self.approval_engine.request_approval(
                execution_id=f"dev_{project_id}",
                action_type=action,
                tenant_id=tenant_id,
            )
            dec = DeveloperAccessDecision(
                action=action,
                tenant_id=tenant_id,
                decision=DeveloperDecisionType.REQUIRE_APPROVAL,
                approval_request_id=appr.request_id,
                reason=f"High-risk action '{action}' requires administrator approval",
            )
            logger.info(f"[DEVELOPER GOVERNANCE] Action '{action}' REQUIRES_APPROVAL -> Approval '{appr.request_id}'")
            return dec

        return DeveloperAccessDecision(action=action, tenant_id=tenant_id, decision=DeveloperDecisionType.ALLOW)
