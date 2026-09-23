"""Model Remediation Intelligence (Phase 5.44)."""

import logging
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List

from pydantic import BaseModel, Field

from app.model_intelligence.exceptions import CrossTenantModelIntelligenceException, ModelRemediationBlockedException
from app.platform_contracts.delegation import DelegationRequest, DelegationTarget

logger = logging.getLogger(__name__)


class ModelRemediationPriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ModelRemediationStatus(str, Enum):
    DRAFT = "DRAFT"
    APPROVED = "APPROVED"
    PENDING_DELEGATION = "PENDING_DELEGATION"
    EXECUTED = "EXECUTED"
    FAILED = "FAILED"


class ModelRemediationAction(BaseModel):
    action_id: str
    action_name: str  # e.g., "rollback_recommendation", "retraining_recommendation", "traffic_reduction_recommendation"
    target_resource_id: str
    target_resource_type: str = "MODEL"
    payload: Dict[str, Any] = Field(default_factory=dict)


class ModelRemediationPlan(BaseModel):
    plan_id: str
    model_id: str
    tenant_id: str
    priority: ModelRemediationPriority
    status: ModelRemediationStatus = ModelRemediationStatus.DRAFT
    actions: List[ModelRemediationAction] = Field(default_factory=list)
    delegation_requests: List[DelegationRequest] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ModelRemediationManager:
    """Manages remediation planning and ensures delegation-only execution via DelegationRequest."""

    def __init__(self) -> None:
        self._plans: Dict[str, ModelRemediationPlan] = {}

    def create_plan(
        self,
        model_id: str,
        tenant_id: str,
        priority: ModelRemediationPriority,
        actions: List[ModelRemediationAction],
    ) -> ModelRemediationPlan:
        plan_id = f"mrem-{uuid.uuid4().hex[:8]}"
        plan = ModelRemediationPlan(
            plan_id=plan_id,
            model_id=model_id,
            tenant_id=tenant_id,
            priority=priority,
            actions=actions,
        )
        self._plans[plan_id] = plan
        logger.info(
            f"[MODEL REMEDIATION] Created plan {plan_id} for model {model_id} (Tenant: {tenant_id}) Priority: {priority}"
        )
        return plan

    def execute_plan_via_delegation(
        self,
        plan_id: str,
        tenant_id: str,
    ) -> ModelRemediationPlan:
        plan = self.get_plan(plan_id, tenant_id)
        if plan.status == ModelRemediationStatus.EXECUTED:
            raise ModelRemediationBlockedException(f"Plan '{plan_id}' has already been executed.")

        del_requests = []
        for act in plan.actions:
            del_req = DelegationRequest(
                tenant_id=tenant_id,
                target=DelegationTarget.APPLICATION_PLATFORM,
                action=act.action_name,
                payload=act.payload,
            )
            del_requests.append(del_req)

        plan.delegation_requests = del_requests
        plan.status = ModelRemediationStatus.PENDING_DELEGATION
        logger.info(f"[MODEL REMEDIATION] Generated {len(del_requests)} DelegationRequest objects for plan {plan_id}")
        return plan

    def get_plan(self, plan_id: str, tenant_id: str) -> ModelRemediationPlan:
        plan = self._plans.get(plan_id)
        if not plan:
            raise ValueError(f"Remediation plan '{plan_id}' not found.")
        if plan.tenant_id != tenant_id:
            raise CrossTenantModelIntelligenceException()
        return plan
