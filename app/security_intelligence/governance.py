"""Security Governance Orchestration Subsystem (Phase 5.32)."""

from typing import Optional

from app.approvals.approval_engine import ApprovalEngine
from app.governance_platform.policy_evaluation import UnifiedPolicyEvaluator
from app.governance_platform.risk import RiskManager
from app.platform_contracts.governance import GovernanceDecision, GovernanceDecisionReason, GovernanceDecisionStatus
from app.security_intelligence.remediation import SecurityRemediationPlan, SecurityRemediationPriority


class SecurityGovernanceEngine:
    """Evaluates security policy compliance and triggers mandatory human approval for high/critical remediations."""

    def __init__(
        self,
        policy_evaluator: Optional[UnifiedPolicyEvaluator] = None,
        risk_manager: Optional[RiskManager] = None,
        approval_engine: Optional[ApprovalEngine] = None,
    ) -> None:
        self.policy_evaluator = policy_evaluator or UnifiedPolicyEvaluator()
        self.risk_manager = risk_manager or RiskManager()
        self.approval_engine = approval_engine or ApprovalEngine()

    def evaluate_remediation_governance(self, tenant_id: str, plan: SecurityRemediationPlan) -> GovernanceDecision:
        is_high_risk = plan.priority in (SecurityRemediationPriority.HIGH, SecurityRemediationPriority.CRITICAL)

        if is_high_risk:
            self.approval_engine.request_approval(
                execution_id=plan.plan_id,
                action_type="HIGH_RISK_SECURITY_REMEDIATION",
                tenant_id=tenant_id,
                requester="security_intelligence_platform",
            )
            return GovernanceDecision(
                tenant_id=tenant_id,
                subject_type="SECURITY_REMEDIATION_PLAN",
                subject_id=plan.plan_id,
                status=GovernanceDecisionStatus.REQUIRE_APPROVAL,
                reasons=[
                    GovernanceDecisionReason(
                        code="HIGH_RISK_SECURITY_APPROVAL_REQUIRED",
                        message="Human approval required for high-risk security remediation",
                    )
                ],
            )

        return GovernanceDecision(
            tenant_id=tenant_id,
            subject_type="SECURITY_REMEDIATION_PLAN",
            subject_id=plan.plan_id,
            status=GovernanceDecisionStatus.ALLOW,
            reasons=[GovernanceDecisionReason(code="AUTO_APPROVED", message="Low/medium risk security remediation")],
        )
