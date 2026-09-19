"""Lifecycle Governance Orchestration Subsystem (Phase 5.33)."""

from typing import Optional

from app.approvals.approval_engine import ApprovalEngine
from app.governance_platform.policy_evaluation import UnifiedPolicyEvaluator
from app.governance_platform.risk import RiskManager
from app.orchestration.human_tasks import HumanTaskManager
from app.platform_contracts.governance import GovernanceDecision, GovernanceDecisionReason, GovernanceDecisionStatus


class LifecycleGovernanceEngine:
    """Orchestrates AI lifecycle policy evaluation and maps outcomes to GovernanceDecision contracts."""

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

    def evaluate_lifecycle_governance(
        self,
        tenant_id: str,
        asset_id: str,
        action_type: str = "PROMOTION",
        has_hard_gate_failure: bool = False,
        requires_approval: bool = False,
    ) -> GovernanceDecision:
        if has_hard_gate_failure:
            return GovernanceDecision(
                tenant_id=tenant_id,
                subject_type="AI_ASSET_LIFECYCLE",
                subject_id=asset_id,
                status=GovernanceDecisionStatus.BLOCK,
                reasons=[
                    GovernanceDecisionReason(
                        code="HARD_GATE_FAILURE",
                        message="Lifecycle promotion blocked due to hard governance gate failure",
                    )
                ],
            )

        if requires_approval:
            self.approval_engine.request_approval(
                execution_id=asset_id,
                action_type=action_type,
                tenant_id=tenant_id,
                requester="ai_lifecycle_platform",
            )
            return GovernanceDecision(
                tenant_id=tenant_id,
                subject_type="AI_ASSET_LIFECYCLE",
                subject_id=asset_id,
                status=GovernanceDecisionStatus.REQUIRE_APPROVAL,
                reasons=[
                    GovernanceDecisionReason(code="APPROVAL_REQUIRED", message="Operation requires human approval")
                ],
            )

        return GovernanceDecision(
            tenant_id=tenant_id,
            subject_type="AI_ASSET_LIFECYCLE",
            subject_id=asset_id,
            status=GovernanceDecisionStatus.ALLOW,
            reasons=[GovernanceDecisionReason(code="GOVERNANCE_PASSED", message="Lifecycle operation permitted")],
        )
