"""Reliability Governance & Human Approval Integration (Phase 5.31)."""

from typing import Optional

from app.approvals.approval_engine import ApprovalEngine
from app.governance_platform.policy_evaluation import UnifiedPolicyEvaluator
from app.governance_platform.risk import RiskManager
from app.orchestration.human_tasks import HumanTaskManager
from app.platform_contracts.governance import GovernanceDecision, GovernanceDecisionReason, GovernanceDecisionStatus
from app.reliability_platform.remediation import RemediationPlan, RemediationRisk


class ReliabilityGovernanceEngine:
    """Evaluates policies and triggers mandatory human approval for high/critical remediations."""

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

    def evaluate_remediation(self, tenant_id: str, plan: RemediationPlan) -> GovernanceDecision:
        has_high_risk = any(a.risk in (RemediationRisk.HIGH, RemediationRisk.CRITICAL) for a in plan.actions)

        if has_high_risk:
            # Trigger approval requirement
            self.approval_engine.request_approval(
                execution_id=plan.plan_id,
                action_type="HIGH_RISK_REMEDIATION",
                tenant_id=tenant_id,
                requester="reliability_platform",
            )
            return GovernanceDecision(
                tenant_id=tenant_id,
                subject_type="REMEDIATION_PLAN",
                subject_id=plan.plan_id,
                status=GovernanceDecisionStatus.REQUIRE_APPROVAL,
                reasons=[
                    GovernanceDecisionReason(
                        code="HIGH_RISK_APPROVAL_REQUIRED", message="Human approval required for high-risk action"
                    )
                ],
            )

        return GovernanceDecision(
            tenant_id=tenant_id,
            subject_type="REMEDIATION_PLAN",
            subject_id=plan.plan_id,
            status=GovernanceDecisionStatus.ALLOW,
            reasons=[GovernanceDecisionReason(code="AUTO_APPROVED", message="Remediation risk is low/medium")],
        )
