"""Model Intelligence Governance Engine (Phase 5.44)."""

import logging
from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.governance_platform.policy_evaluation import UnifiedPolicyEvaluator
from app.governance_platform.risk import RiskManager
from app.approvals.approval_engine import ApprovalEngine
from app.orchestration.human_tasks import HumanTaskManager
from app.model_intelligence.exceptions import HighRiskModelActionRequiresApprovalException, ModelGovernanceBlockedException

logger = logging.getLogger(__name__)


class ModelGovernanceDecisionStatus(str, Enum):
    ALLOW = "ALLOW"
    DENY = "DENY"
    REQUIRE_APPROVAL = "REQUIRE_APPROVAL"
    RESTRICT = "RESTRICT"
    BLOCK = "BLOCK"


class ModelGovernanceDecision(BaseModel):
    decision_id: str
    action_type: str
    model_id: str
    tenant_id: str
    status: ModelGovernanceDecisionStatus
    reasoning: str
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ModelIntelligenceGovernanceEngine:
    """Governance engine composing UnifiedPolicyEvaluator, RiskManager, ApprovalEngine, and HumanTaskManager."""

    HIGH_RISK_ACTIONS = {
        "production_model_rollback",
        "model_disablement",
        "production_deployment_changes",
        "retraining_actions",
        "model_provider_replacement",
        "traffic_routing_changes",
        "safety_policy_changes",
        "model_version_retirement",
    }

    def __init__(self) -> None:
        self.policy_evaluator = UnifiedPolicyEvaluator()
        self.risk_manager = RiskManager()
        self.approval_engine = ApprovalEngine()
        self.task_manager = HumanTaskManager()

    def evaluate_action(
        self,
        action_type: str,
        model_id: str,
        tenant_id: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> ModelGovernanceDecision:
        dec_id = f"gdec-{uuid.uuid4().hex[:8]}"

        # Check high-risk actions
        if action_type.lower() in [a.lower() for a in self.HIGH_RISK_ACTIONS]:
            logger.warning(f"[MODEL GOVERNANCE] Action '{action_type}' for model '{model_id}' is high-risk -> REQUIRE_APPROVAL")
            return ModelGovernanceDecision(
                decision_id=dec_id,
                action_type=action_type,
                model_id=model_id,
                tenant_id=tenant_id,
                status=ModelGovernanceDecisionStatus.REQUIRE_APPROVAL,
                reasoning=f"High-risk action '{action_type}' requires human approval.",
            )

        # Policy evaluation check
        ctx = context or {}
        policy_eval_result = self.policy_evaluator.evaluate_request(action=action_type, resource_id=model_id, tenant_id=tenant_id, context=ctx)
        if not policy_eval_result.allow:
            return ModelGovernanceDecision(
                decision_id=dec_id,
                action_type=action_type,
                model_id=model_id,
                tenant_id=tenant_id,
                status=ModelGovernanceDecisionStatus.DENY,
                reasoning="UnifiedPolicyEvaluator denied action.",
            )

        return ModelGovernanceDecision(
            decision_id=dec_id,
            action_type=action_type,
            model_id=model_id,
            tenant_id=tenant_id,
            status=ModelGovernanceDecisionStatus.ALLOW,
            reasoning="Governance evaluation passed successfully.",
        )
