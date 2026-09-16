"""Identity Governance Engine composing policy, risk, approval, and task primitives."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

from app.approvals.approval_engine import ApprovalEngine
from app.governance_platform.policy_evaluation import UnifiedPolicyEvaluator
from app.governance_platform.risk import RiskManager
from app.orchestration.human_tasks import HumanTaskManager


class IdentityGovernanceOutcome(str, Enum):
    ALLOW = "ALLOW"
    DENY = "DENY"
    REQUIRE_APPROVAL = "REQUIRE_APPROVAL"
    RESTRICT = "RESTRICT"
    BLOCK = "BLOCK"


class IdentityGovernanceRequest(BaseModel):
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    action_type: str  # PRIVILEGED_ESCALATION, ADMIN_ROLE_ASSIGNMENT, EMERGENCY_ACCESS, MFA_DISABLEMENT, IDENTITY_DEACTIVATION, BULK_REVOCATION, SERVICE_ACCOUNT_ESCALATION, AGENT_PRIVILEGE_EXPANSION, CROSS_DOMAIN_GRANT, POLICY_OVERRIDE
    target_identity_id: str
    risk_score: float = 0.0
    context: Dict[str, Any] = Field(default_factory=dict)


class IdentityGovernanceResult(BaseModel):
    result_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    target_identity_id: str
    outcome: IdentityGovernanceOutcome
    requires_human_approval: bool = False
    reasoning: str = ""
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class IdentityGovernanceEngine:
    """Evaluates identity governance requests using platform policy, risk, and approval primitives."""

    HIGH_RISK_ACTIONS = {
        "PRIVILEGED_ESCALATION",
        "ADMIN_ROLE_ASSIGNMENT",
        "EMERGENCY_ACCESS",
        "MFA_DISABLEMENT",
        "IDENTITY_DEACTIVATION",
        "BULK_REVOCATION",
        "SERVICE_ACCOUNT_ESCALATION",
        "AGENT_PRIVILEGE_EXPANSION",
        "CROSS_DOMAIN_GRANT",
        "POLICY_OVERRIDE",
    }

    def __init__(
        self,
        policy_evaluator: Optional[UnifiedPolicyEvaluator] = None,
        risk_manager: Optional[RiskManager] = None,
        approval_engine: Optional[ApprovalEngine] = None,
        task_manager: Optional[HumanTaskManager] = None,
    ) -> None:
        self.policy_evaluator = policy_evaluator or UnifiedPolicyEvaluator()
        self.risk_manager = risk_manager or RiskManager()
        self.approval_engine = approval_engine or ApprovalEngine()
        self.task_manager = task_manager or HumanTaskManager()

    def evaluate_action(
        self,
        request: IdentityGovernanceRequest,
    ) -> IdentityGovernanceResult:
        action_upper = request.action_type.upper()

        if action_upper in self.HIGH_RISK_ACTIONS or request.risk_score >= 0.7:
            return IdentityGovernanceResult(
                tenant_id=request.tenant_id,
                target_identity_id=request.target_identity_id,
                outcome=IdentityGovernanceOutcome.REQUIRE_APPROVAL,
                requires_human_approval=True,
                reasoning=f"High-risk identity action '{request.action_type}' requires human governance approval.",
            )

        if request.risk_score >= 0.4:
            return IdentityGovernanceResult(
                tenant_id=request.tenant_id,
                target_identity_id=request.target_identity_id,
                outcome=IdentityGovernanceOutcome.RESTRICT,
                requires_human_approval=False,
                reasoning=f"Action '{request.action_type}' restricted due to moderate risk ({request.risk_score}).",
            )

        return IdentityGovernanceResult(
            tenant_id=request.tenant_id,
            target_identity_id=request.target_identity_id,
            outcome=IdentityGovernanceOutcome.ALLOW,
            requires_human_approval=False,
            reasoning=f"Action '{request.action_type}' allowed.",
        )
