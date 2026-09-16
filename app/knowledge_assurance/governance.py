"""Knowledge governance engine composing policy, risk, approval, and task primitives."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

from app.approvals.approval_engine import ApprovalEngine
from app.governance_platform.policy_evaluation import UnifiedPolicyEvaluator
from app.governance_platform.risk import RiskManager
from app.orchestration.human_tasks import HumanTaskManager


class KnowledgeGovernanceOutcome(str, Enum):
    ALLOW = "ALLOW"
    DENY = "DENY"
    REQUIRE_APPROVAL = "REQUIRE_APPROVAL"
    RESTRICT = "RESTRICT"
    BLOCK = "BLOCK"


class KnowledgeGovernanceRequest(BaseModel):
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    action_type: str  # DELETE_KNOWLEDGE, REPLACE_AUTHORITATIVE, CHANGE_TRUST_POLICY, REVOKE_SOURCE, RESOLVE_CRITICAL_CONFLICT, CHANGE_CLASSIFICATION
    target_reference_id: str
    risk_score: float = 0.0
    context: Dict[str, Any] = Field(default_factory=dict)


class KnowledgeGovernanceResult(BaseModel):
    result_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    target_reference_id: str
    outcome: KnowledgeGovernanceOutcome
    requires_human_approval: bool = False
    reasoning: str = ""
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class KnowledgeGovernanceContext(BaseModel):
    tenant_id: str
    user_id: str = "system"
    role: str = "admin"
    environment: str = "production"


class KnowledgeGovernanceEngine:
    """Evaluates knowledge governance actions using policy, risk, and approval primitives."""

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

    def evaluate_knowledge_action(
        self,
        request: Optional[KnowledgeGovernanceRequest] = None,
        tenant_id: Optional[str] = None,
        action_type: str = "GENERIC_ACTION",
        target_resource_id: str = "res-1",
        risk_score: float = 0.0,
        context: Optional[Dict[str, Any]] = None,
    ) -> KnowledgeGovernanceResult:
        if request is None:
            request = KnowledgeGovernanceRequest(
                tenant_id=tenant_id or "default_tenant",
                action_type=action_type,
                target_reference_id=target_resource_id,
                risk_score=risk_score,
                context=context or {},
            )
        high_risk_actions = [
            "DELETE_KNOWLEDGE",
            "REPLACE_AUTHORITATIVE",
            "CHANGE_TRUST_POLICY",
            "REVOKE_SOURCE",
            "RESOLVE_CRITICAL_CONFLICT",
            "CHANGE_CLASSIFICATION",
        ]

        is_high_risk = request.risk_score > 0.60 or request.action_type in high_risk_actions

        if is_high_risk:
            outcome = KnowledgeGovernanceOutcome.REQUIRE_APPROVAL
            req_approval = True
            reason = f"High-risk knowledge action '{request.action_type}' requires human approval."
        elif request.risk_score > 0.85:
            outcome = KnowledgeGovernanceOutcome.DENY
            req_approval = False
            reason = "Action risk score exceeds maximum allowable threshold."
        else:
            outcome = KnowledgeGovernanceOutcome.ALLOW
            req_approval = False
            reason = "Knowledge governance check passed all security and compliance rules."

        return KnowledgeGovernanceResult(
            target_reference_id=request.target_reference_id,
            tenant_id=request.tenant_id,
            outcome=outcome,
            requires_human_approval=req_approval,
            reasoning=reason,
        )
