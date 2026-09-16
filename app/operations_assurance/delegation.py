"""Delegated operational execution coordination delegating to platform execution engines."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class OperationalDelegationStatus(str, Enum):
    PENDING = "PENDING"
    QUEUED = "QUEUED"
    EXECUTING = "EXECUTING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class OperationalDelegationAction(BaseModel):
    action_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    action_type: str
    target_engine: str = "PLATFORM_OPERATIONS"
    parameters: Dict[str, Any] = Field(default_factory=dict)
    requires_approval: bool = True


class OperationalDelegationPlan(BaseModel):
    delegation_plan_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    service_id: str
    actions: List[OperationalDelegationAction] = Field(default_factory=list)
    status: OperationalDelegationStatus = OperationalDelegationStatus.PENDING
    delegation_request_ids: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class OperationsDelegationManager:
    """Coordinates delegated operational actions using DelegationRequest contracts."""

    def __init__(self) -> None:
        self._plans: Dict[str, Dict[str, OperationalDelegationPlan]] = {}  # tenant_id -> {plan_id: plan}

    def create_delegation_plan(
        self,
        tenant_id: str,
        service_id: str,
        actions: List[OperationalDelegationAction],
    ) -> OperationalDelegationPlan:
        # Generate delegation request IDs for each action
        del_ids = [f"delreq_{uuid.uuid4().hex[:12]}" for _ in actions]

        plan = OperationalDelegationPlan(
            tenant_id=tenant_id,
            service_id=service_id,
            actions=actions,
            status=OperationalDelegationStatus.PENDING,
            delegation_request_ids=del_ids,
        )

        if tenant_id not in self._plans:
            self._plans[tenant_id] = {}
        self._plans[tenant_id][plan.delegation_plan_id] = plan
        return plan

    def list_delegation_plans(self, tenant_id: str, service_id: Optional[str] = None) -> List[OperationalDelegationPlan]:
        tenant_plans = self._plans.get(tenant_id, {})
        if service_id:
            return [p for p in tenant_plans.values() if p.service_id == service_id]
        return list(tenant_plans.values())
