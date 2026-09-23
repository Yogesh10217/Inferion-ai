"""Delegated Action Coordination for Model Intelligence (Phase 5.44)."""

import logging
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List

from pydantic import BaseModel, Field

from app.model_intelligence.exceptions import CrossTenantModelIntelligenceException
from app.platform_contracts.delegation import DelegationRequest, DelegationTarget

logger = logging.getLogger(__name__)


class ModelDelegationStatus(str, Enum):
    PENDING = "PENDING"
    DISPATCHED = "DISPATCHED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class ModelDelegationAction(BaseModel):
    action_id: str
    target_system: str
    action_type: str
    payload: Dict[str, Any] = Field(default_factory=dict)


class ModelDelegationPlan(BaseModel):
    delegation_id: str
    model_id: str
    tenant_id: str
    status: ModelDelegationStatus = ModelDelegationStatus.PENDING
    actions: List[ModelDelegationAction] = Field(default_factory=list)
    delegation_requests: List[DelegationRequest] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ModelDelegationManager:
    """Coordinates delegated action requests without executing direct mutations."""

    def __init__(self) -> None:
        self._delegations: Dict[str, ModelDelegationPlan] = {}

    def create_delegation_plan(
        self,
        model_id: str,
        tenant_id: str,
        actions: List[ModelDelegationAction],
    ) -> ModelDelegationPlan:
        del_id = f"mdel-{uuid.uuid4().hex[:8]}"

        del_reqs = [
            DelegationRequest(
                tenant_id=tenant_id,
                target=DelegationTarget.APPLICATION_PLATFORM,
                action=a.action_type,
                payload=a.payload,
            )
            for a in actions
        ]

        plan = ModelDelegationPlan(
            delegation_id=del_id,
            model_id=model_id,
            tenant_id=tenant_id,
            status=ModelDelegationStatus.DISPATCHED,
            actions=actions,
            delegation_requests=del_reqs,
        )

        self._delegations[del_id] = plan
        logger.info(f"[MODEL DELEGATION] Created delegation plan {del_id} with {len(del_reqs)} DelegationRequests")
        return plan

    def get_delegation_plan(self, delegation_id: str, tenant_id: str) -> ModelDelegationPlan:
        plan = self._delegations.get(delegation_id)
        if not plan:
            raise ValueError(f"Delegation plan '{delegation_id}' not found.")
        if plan.tenant_id != tenant_id:
            raise CrossTenantModelIntelligenceException()
        return plan
