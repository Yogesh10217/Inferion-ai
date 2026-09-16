"""Event Governance Engine Subsystem (Phase 5.34)."""

from typing import Optional

from app.approvals.approval_engine import ApprovalEngine
from app.governance_platform.policy_evaluation import UnifiedPolicyEvaluator
from app.governance_platform.risk import RiskManager
from app.orchestration.human_tasks import HumanTaskManager
from app.platform_contracts.governance import GovernanceDecision, GovernanceDecisionReason, GovernanceDecisionStatus


class EventGovernanceEngine:
    """Orchestrates event automation governance and evaluates mandatory human approval gates."""

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

    def evaluate_automation_governance(
        self,
        tenant_id: str,
        event_id: str,
        action_name: str = "REQUEST_SECURITY_REMEDIATION",
        is_high_risk: bool = False,
        attempts_direct_mutation: bool = False,
    ) -> GovernanceDecision:
        if attempts_direct_mutation:
            return GovernanceDecision(
                tenant_id=tenant_id,
                subject_type="EVENT_AUTOMATION",
                subject_id=event_id,
                status=GovernanceDecisionStatus.BLOCK,
                reasons=[GovernanceDecisionReason(code="DIRECT_MUTATION_FORBIDDEN", message="Direct infrastructure mutation is strictly forbidden")],
            )

        if is_high_risk:
            self.approval_engine.request_approval(
                execution_id=event_id,
                action_type=action_name,
                tenant_id=tenant_id,
                requester="event_intelligence",
            )
            return GovernanceDecision(
                tenant_id=tenant_id,
                subject_type="EVENT_AUTOMATION",
                subject_id=event_id,
                status=GovernanceDecisionStatus.REQUIRE_APPROVAL,
                reasons=[GovernanceDecisionReason(code="HIGH_RISK_AUTOMATION", message="High risk automation requires human approval")],
            )

        return GovernanceDecision(
            tenant_id=tenant_id,
            subject_type="EVENT_AUTOMATION",
            subject_id=event_id,
            status=GovernanceDecisionStatus.ALLOW,
            reasons=[GovernanceDecisionReason(code="GOVERNANCE_PASSED", message="Automation permitted")],
        )
