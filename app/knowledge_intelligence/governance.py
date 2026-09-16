"""Knowledge Governance Orchestration Subsystem (Phase 5.35)."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field

from app.approvals.approval_engine import ApprovalEngine
from app.governance_platform.policy_evaluation import UnifiedPolicyEvaluator
from app.governance_platform.risk import RiskManager
from app.orchestration.human_tasks import HumanTaskManager
from app.platform_contracts.governance import (
    GovernanceDecisionReason,
    GovernanceDecisionStatus,
)


class KnowledgeGovernanceStatus(str, Enum):
    ALLOW = "ALLOW"
    WARN = "WARN"
    REQUIRE_APPROVAL = "REQUIRE_APPROVAL"
    RESTRICT = "RESTRICT"
    BLOCK = "BLOCK"


class KnowledgeGovernanceRequirement(BaseModel):
    requirement_id: str = Field(default_factory=lambda: f"kgovreq_{uuid.uuid4().hex[:8]}")
    description: str
    is_mandatory: bool = True


class KnowledgeGovernanceDecision(BaseModel):
    decision_id: str = Field(default_factory=lambda: f"kgovdec_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    target_id: str
    status: GovernanceDecisionStatus
    reasons: List[GovernanceDecisionReason] = Field(default_factory=list)
    requires_approval: bool = False
    approval_request_id: Optional[str] = None
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class KnowledgeGovernanceEngine:
    """Orchestrates knowledge governance decisions using UnifiedPolicyEvaluator, RiskManager, and ApprovalEngine."""

    def __init__(
        self,
        policy_evaluator: Optional[UnifiedPolicyEvaluator] = None,
        risk_manager: Optional[RiskManager] = None,
        approval_engine: Optional[ApprovalEngine] = None,
        human_task_manager: Optional[HumanTaskManager] = None,
    ) -> None:
        self.policy_evaluator = policy_evaluator or UnifiedPolicyEvaluator()
        self.risk_manager = risk_manager or RiskManager()
        self.approval_engine = approval_engine or ApprovalEngine()
        self.human_task_manager = human_task_manager or HumanTaskManager()

    def evaluate_action_governance(
        self,
        tenant_id: str,
        target_id: str,
        action_name: str,
        is_high_risk: bool = False,
        attempts_direct_mutation: bool = False,
        classification_restricted: bool = False,
    ) -> KnowledgeGovernanceDecision:
        if attempts_direct_mutation:
            reason = GovernanceDecisionReason(code="DIRECT_MUTATION_FORBIDDEN", message="Direct knowledge mutation forbidden. Use delegation.", severity="CRITICAL")
            return KnowledgeGovernanceDecision(
                tenant_id=tenant_id,
                target_id=target_id,
                status=GovernanceDecisionStatus.BLOCK,
                reasons=[reason],
            )

        if is_high_risk or classification_restricted:
            req = self.approval_engine.request_approval(
                execution_id=target_id,
                action_type=action_name,
                tenant_id=tenant_id,
                requester="KnowledgeGovernanceEngine",
            )
            reason = GovernanceDecisionReason(code="HIGH_RISK_REQUIRES_APPROVAL", message="Action is high-risk or restricted. Human approval requested.", severity="HIGH")
            return KnowledgeGovernanceDecision(
                tenant_id=tenant_id,
                target_id=target_id,
                status=GovernanceDecisionStatus.REQUIRE_APPROVAL,
                reasons=[reason],
                requires_approval=True,
                approval_request_id=req.request_id,
            )

        reason = GovernanceDecisionReason(code="POLICY_PASSED", message="Knowledge action permitted.", severity="INFO")
        return KnowledgeGovernanceDecision(
            tenant_id=tenant_id,
            target_id=target_id,
            status=GovernanceDecisionStatus.ALLOW,
            reasons=[reason],
        )
