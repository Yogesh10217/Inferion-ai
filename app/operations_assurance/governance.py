"""Operations Governance Engine composing policy, risk, approval, and human task primitives."""

from datetime import datetime, timezone
from enum import Enum
from typing import Dict, Any, List, Optional
import uuid
from pydantic import BaseModel, Field

from app.operations_assurance.exceptions import CrossTenantOperationsAssuranceException, HighRiskOperationalActionRequiresApprovalException
from app.approvals.approval_engine import ApprovalEngine
from app.governance_platform.risk import RiskManager
from app.governance_platform.policy_evaluation import UnifiedPolicyEvaluator
from app.orchestration.human_tasks import HumanTaskManager


class OperationsGovernanceOutcome(str, Enum):
    ALLOW = "ALLOW"
    DENY = "DENY"
    RESTRICT = "RESTRICT"
    BLOCK = "BLOCK"
    REQUIRE_APPROVAL = "REQUIRE_APPROVAL"


class OperationsGovernanceRequest(BaseModel):
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    action_type: str  # SERVICE_RESTART, ROLLBACK, INFRASTRUCTURE_SCALE, DISASTER_RECOVERY, FAILOVER, TRAFFIC_REROUTE
    target_resource_id: str
    risk_score: float = 0.0
    context: Dict[str, Any] = Field(default_factory=dict)


class OperationsGovernanceResult(BaseModel):
    result_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    target_resource_id: str
    outcome: OperationsGovernanceOutcome
    requires_human_approval: bool = False
    reasoning: str = ""
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class OperationsGovernanceEngine:
    """Evaluates operational actions against governance rules, policy, and risk scoring."""

    HIGH_RISK_ACTIONS = {
        "SERVICE_RESTART",
        "PRODUCTION_SERVICE_RESTART",
        "ROLLBACK",
        "PRODUCTION_ROLLBACK",
        "INFRASTRUCTURE_SCALE",
        "DISASTER_RECOVERY",
        "REGIONAL_FAILOVER",
        "CRITICAL_DEPENDENCY_SHUTDOWN",
        "TRAFFIC_REROUTE",
        "PRODUCTION_TRAFFIC_REROUTE",
        "CAPACITY_OVERRIDE",
        "EMERGENCY_OPERATIONAL_ACTION",
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
        request: OperationsGovernanceRequest,
    ) -> OperationsGovernanceResult:
        action_upper = request.action_type.upper()

        if action_upper in self.HIGH_RISK_ACTIONS or request.risk_score >= 0.7:
            return OperationsGovernanceResult(
                tenant_id=request.tenant_id,
                target_resource_id=request.target_resource_id,
                outcome=OperationsGovernanceOutcome.REQUIRE_APPROVAL,
                requires_human_approval=True,
                reasoning=f"High-risk operational action '{request.action_type}' requires explicit human approval.",
            )

        if request.risk_score >= 0.4:
            return OperationsGovernanceResult(
                tenant_id=request.tenant_id,
                target_resource_id=request.target_resource_id,
                outcome=OperationsGovernanceOutcome.RESTRICT,
                requires_human_approval=False,
                reasoning=f"Operational action '{request.action_type}' restricted due to moderate risk ({request.risk_score}).",
            )

        return OperationsGovernanceResult(
            tenant_id=request.tenant_id,
            target_resource_id=request.target_resource_id,
            outcome=OperationsGovernanceOutcome.ALLOW,
            requires_human_approval=False,
            reasoning=f"Operational action '{request.action_type}' allowed.",
        )
