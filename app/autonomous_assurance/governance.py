"""
Autonomous Assurance Governance Engine Subsystem.
Evaluates workflow proposals against active governance policies, risk thresholds, and approval requirements.
"""

from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.governance_platform.policy_evaluation import UnifiedPolicyEvaluator
from app.governance_platform.risk import RiskManager
from app.approvals.approval_engine import ApprovalEngine
from app.orchestration.human_tasks import HumanTaskManager


class GovernanceEvaluationStatus(str, Enum):
    ALLOW = "ALLOW"
    DENY = "DENY"
    REQUIRE_APPROVAL = "REQUIRE_APPROVAL"
    ADVISORY_ONLY = "ADVISORY_ONLY"


class AutonomousGovernanceEvaluation(BaseModel):
    evaluation_id: str = Field(default_factory=lambda: f"gov_{uuid.uuid4().hex[:12]}")
    workflow_id: str
    tenant_id: str
    status: GovernanceEvaluationStatus = GovernanceEvaluationStatus.ALLOW
    requires_approval: bool = False
    approval_request_id: Optional[str] = None
    reason: str
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AutonomousAssuranceGovernanceEngine:
    """Evaluates workflows against enterprise governance policies."""

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

    def evaluate_workflow_governance(
        self,
        workflow_id: str,
        tenant_id: str,
        risk_score: float = 20.0,
        trust_score: float = 90.0,
        action_name: str = "DELEGATE_ACTION",
    ) -> AutonomousGovernanceEvaluation:
        requires_approval = (risk_score >= 50.0) or (trust_score < 70.0) or ("RESTART" in action_name.upper()) or ("DISABLE" in action_name.upper())

        if requires_approval:
            status = GovernanceEvaluationStatus.REQUIRE_APPROVAL
            reason = f"Workflow '{workflow_id}' carries Risk {risk_score:.1f}, Trust {trust_score:.1f}, or high-risk action '{action_name}'. Human approval required."
            app_req = self.approval_engine.request_approval(
                execution_id=workflow_id,
                action_type="AUTONOMOUS_WORKFLOW_APPROVAL",
                requester="autonomous_assurance_engine",
                tenant_id=tenant_id,
                payload={"workflow_id": workflow_id, "risk_score": risk_score},
            )
            app_id = app_req.request_id
        else:
            status = GovernanceEvaluationStatus.ALLOW
            reason = f"Workflow '{workflow_id}' approved for coordination within autonomous limits."
            app_id = None

        return AutonomousGovernanceEvaluation(
            workflow_id=workflow_id,
            tenant_id=tenant_id,
            status=status,
            requires_approval=requires_approval,
            approval_request_id=app_id,
            reason=reason,
        )
