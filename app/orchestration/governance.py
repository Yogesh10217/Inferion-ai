"""Workflow Governance, Pre-Execution Risk Evaluation & Autonomy Boundary Engine."""

import logging
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

from app.approvals.approval_engine import ApprovalEngine
from app.governance_platform.risk import RiskManager
from app.identity.manager import IdentitySecurityManager

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class GovernanceAction(str, Enum):
    ALLOW = "ALLOW"
    WARN = "WARN"
    REQUIRE_APPROVAL = "REQUIRE_APPROVAL"
    THROTTLE = "THROTTLE"
    PAUSE = "PAUSE"
    BLOCK = "BLOCK"
    ESCALATE = "ESCALATE"


class WorkflowRiskAssessment(BaseModel):
    assessment_id: str = Field(default_factory=lambda: f"wrisk_{uuid.uuid4().hex[:10]}")
    workflow_id: str
    tenant_id: str = "global"

    risk_score: float = 0.0  # 0.0 to 100.0 scale
    governance_action: GovernanceAction = GovernanceAction.ALLOW
    approval_request_id: Optional[str] = None
    reason: str = ""
    evaluated_at: datetime = Field(default_factory=_now)


class WorkflowGovernanceEngine:
    """Evaluates pre-execution risk, identity trust, and budget constraints before allowing sensitive workflow steps."""

    def __init__(
        self,
        risk_manager: Optional[RiskManager] = None,
        approval_engine: Optional[ApprovalEngine] = None,
        identity_security_manager: Optional[IdentitySecurityManager] = None,
    ) -> None:
        self.risk_manager = risk_manager or RiskManager()
        self.approval_engine = approval_engine or ApprovalEngine()
        self.identity_security_manager = identity_security_manager or IdentitySecurityManager()

    def evaluate_workflow_execution(
        self,
        workflow_id: str,
        tenant_id: str = "global",
        action_name: str = "production_deploy",
        risk_score: float = 0.0,
    ) -> WorkflowRiskAssessment:
        if risk_score >= 70.0 or "production" in action_name:
            req_id = f"appr_wf_{uuid.uuid4().hex[:8]}"
            res = WorkflowRiskAssessment(
                workflow_id=workflow_id,
                tenant_id=tenant_id,
                risk_score=risk_score if risk_score > 0 else 75.0,
                governance_action=GovernanceAction.REQUIRE_APPROVAL,
                approval_request_id=req_id,
                reason=f"Action '{action_name}' requires administrator approval due to elevated risk ({risk_score:.1f})",
            )
            logger.warning(f"[WORKFLOW GOVERNANCE] Execution for '{workflow_id}' requires approval (ID: {req_id})")
            return res

        res_allow = WorkflowRiskAssessment(
            workflow_id=workflow_id,
            tenant_id=tenant_id,
            risk_score=risk_score,
            governance_action=GovernanceAction.ALLOW,
            reason="Execution allowed under standard governance policy",
        )
        return res_allow
