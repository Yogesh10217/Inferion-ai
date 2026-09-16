"""Delegated Identity Actions."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List

from pydantic import BaseModel, Field

from app.identity_assurance.exceptions import CrossTenantIdentityAssuranceException
from app.platform_contracts.delegation import DelegationRequest, DelegationTarget


class IdentityDelegationStatus(str, Enum):
    PLANNED = "PLANNED"
    SUBMITTED = "SUBMITTED"
    APPROVED = "APPROVED"
    EXECUTING = "EXECUTING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class IdentityDelegationAction(BaseModel):
    action_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    action_type: str  # REVOKE_PERMISSION, ROTATE_SECRET, DISABLE_IDENTITY, UPDATE_ROLE
    target_identity_id: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    reasoning: str = ""


class IdentityDelegationPlan(BaseModel):
    plan_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    actions: List[IdentityDelegationAction] = Field(default_factory=list)
    status: IdentityDelegationStatus = IdentityDelegationStatus.PLANNED
    delegation_requests: List[DelegationRequest] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class IdentityDelegationManager:
    """Manages identity delegation plans. Ensures ZERO direct IAM mutations."""

    def __init__(self) -> None:
        self._plans: Dict[str, IdentityDelegationPlan] = {}

    def create_delegation_plan(
        self,
        tenant_id: str,
        actions: List[IdentityDelegationAction],
    ) -> IdentityDelegationPlan:
        delegation_requests = []
        for action in actions:
            req = DelegationRequest(
                tenant_id=tenant_id,
                target=DelegationTarget.APPLICATION_PLATFORM,
                action=action.action_type,
                payload={
                    "target_identity_id": action.target_identity_id,
                    "parameters": action.parameters,
                    "reasoning": action.reasoning,
                },
            )
            delegation_requests.append(req)

        plan = IdentityDelegationPlan(
            tenant_id=tenant_id,
            actions=actions,
            status=IdentityDelegationStatus.SUBMITTED,
            delegation_requests=delegation_requests,
        )
        self._plans[plan.plan_id] = plan
        return plan

    def get_plan(self, tenant_id: str, plan_id: str) -> IdentityDelegationPlan:
        plan = self._plans.get(plan_id)
        if not plan or plan.tenant_id != tenant_id:
            raise CrossTenantIdentityAssuranceException()
        return plan
