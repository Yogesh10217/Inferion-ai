"""Knowledge Governance, Pre-Retrieval Policy & Masking Subsystem."""

import logging
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

from app.approvals.approval_engine import ApprovalEngine
from app.governance_platform.policy_evaluation import UnifiedPolicyEvaluator
from app.governance_platform.risk import RiskManager
from app.security.authorization import AuthorizationEngine

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class PolicyDecisionType(str, Enum):
    ALLOW = "ALLOW"
    FILTER = "FILTER"
    MASK = "MASK"
    REDACT = "REDACT"
    REQUIRE_APPROVAL = "REQUIRE_APPROVAL"
    BLOCK = "BLOCK"


class KnowledgeAccessDecision(BaseModel):
    decision_id: str = Field(default_factory=lambda: f"kdec_{uuid.uuid4().hex[:10]}")
    identity_id: str
    tenant_id: str = "global"
    policy_decision: PolicyDecisionType = PolicyDecisionType.ALLOW

    approval_request_id: Optional[str] = None
    reason: str = "Pre-retrieval policy evaluated successfully"
    evaluated_at: datetime = Field(default_factory=_now)


class KnowledgeGovernanceEngine:
    """Evaluates pre-retrieval knowledge policies, risk scores, and approval gating."""

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

    def evaluate_access(
        self,
        identity_id: str,
        user_role: str = "viewer",
        tenant_id: str = "global",
        classification: str = "INTERNAL",
    ) -> KnowledgeAccessDecision:
        # High classification / guest -> BLOCK or REQUIRE_APPROVAL
        if classification == "RESTRICTED" and user_role in ("guest", "viewer"):
            dec = KnowledgeAccessDecision(
                identity_id=identity_id,
                tenant_id=tenant_id,
                policy_decision=PolicyDecisionType.BLOCK,
                reason="Restricted knowledge cannot be accessed by viewer/guest role",
            )
            logger.warning(f"[GOVERNANCE ENGINE] Knowledge access BLOCKED for identity '{identity_id}'")
            return dec

        if classification == "SECRET":
            appr = self.approval_engine.request_approval(
                execution_id="access_sec",
                action_type="Secret Knowledge Access Request",
                requester=identity_id,
                tenant_id=tenant_id,
            )
            dec = KnowledgeAccessDecision(
                identity_id=identity_id,
                tenant_id=tenant_id,
                policy_decision=PolicyDecisionType.REQUIRE_APPROVAL,
                approval_request_id=appr.request_id,
                reason="Secret classification requires administrator approval",
            )
            logger.info(
                f"[GOVERNANCE ENGINE] Knowledge access REQUIRES_APPROVAL for identity '{identity_id}' -> Request '{appr.request_id}'"
            )
            return dec

        return KnowledgeAccessDecision(
            identity_id=identity_id, tenant_id=tenant_id, policy_decision=PolicyDecisionType.ALLOW
        )
