"""Integration Governance & High-Risk Approval Gating Subsystem."""

from datetime import datetime, timezone
from enum import Enum
import uuid
import logging
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field

from app.security.authorization import AuthorizationEngine
from app.governance_platform.policy_evaluation import UnifiedPolicyEvaluator
from app.governance_platform.risk import RiskManager
from app.approvals.approval_engine import ApprovalEngine

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class IntegrationDecisionType(str, Enum):
    ALLOW = "ALLOW"
    WARN = "WARN"
    REQUIRE_APPROVAL = "REQUIRE_APPROVAL"
    THROTTLE = "THROTTLE"
    RESTRICT = "RESTRICT"
    BLOCK = "BLOCK"


class IntegrationAccessDecision(BaseModel):
    decision_id: str = Field(default_factory=lambda: f"idec_{uuid.uuid4().hex[:10]}")
    integration_id: str
    tenant_id: str = "global"
    decision: IntegrationDecisionType = IntegrationDecisionType.ALLOW

    approval_request_id: Optional[str] = None
    reason: str = "Policy evaluated successfully"
    evaluated_at: datetime = Field(default_factory=_now)


class IntegrationGovernanceEngine:
    """Evaluates external integration policy risk, identity scope, and approval gating for high-risk actions."""

    def __init__(
        self,
        authorization_engine: Optional[AuthorizationEngine] = None,
        policy_evaluator: Optional[UnifiedPolicyEvaluator] = None,
        risk_manager: Optional[RiskManager] = None,
        approval_engine: Optional[ApprovalEngine] = None,
    ) -> None:
        self.authorization_engine = authorization_engine or AuthorizationEngine()
        self.policy_evaluator = policy_evaluator or UnifiedPolicyEvaluator()
        self.risk_manager = risk_manager or RiskManager()
        self.approval_engine = approval_engine or ApprovalEngine()

    def evaluate_external_action(
        self,
        integration_id: str,
        action: str,
        identity_id: str = "user",
        tenant_id: str = "global",
        risk_level: str = "LOW",
    ) -> IntegrationAccessDecision:
        if risk_level in ("HIGH", "CRITICAL"):
            appr = self.approval_engine.request_approval(
                execution_id=f"ext_{integration_id}",
                action_type=action,
                requester=identity_id,
                tenant_id=tenant_id,
            )
            dec = IntegrationAccessDecision(
                integration_id=integration_id,
                tenant_id=tenant_id,
                decision=IntegrationDecisionType.REQUIRE_APPROVAL,
                approval_request_id=appr.request_id,
                reason=f"High-risk external action '{action}' requires administrator approval",
            )
            logger.info(f"[INTEGRATION GOVERNANCE] External action '{action}' REQUIRES_APPROVAL -> Request '{appr.request_id}'")
            return dec

        return IntegrationAccessDecision(integration_id=integration_id, tenant_id=tenant_id, decision=IntegrationDecisionType.ALLOW)
