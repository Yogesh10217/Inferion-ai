"""Delegated decision action coordination creating DelegationRequest instances."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List

from pydantic import BaseModel, Field

from app.decision_governance.exceptions import CrossTenantDecisionGovernanceException
from app.platform_contracts.delegation import DelegationRequest, DelegationTarget


class DecisionDelegationStatus(str, Enum):
    PENDING = "PENDING"
    DELEGATED = "DELEGATED"
    APPROVED = "APPROVED"
    EXECUTED = "EXECUTED"
    REJECTED = "REJECTED"


class DecisionDelegationAction(BaseModel):
    action_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    target_type: str  # e.g. INFRASTRUCTURE, WORKFLOW, MODEL, DATA
    target_id: str
    action_name: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    requires_approval: bool = False


class DecisionDelegationPlan(BaseModel):
    delegation_plan_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    decision_id: str
    tenant_id: str
    status: DecisionDelegationStatus = DecisionDelegationStatus.PENDING
    actions: List[DecisionDelegationAction] = Field(default_factory=list)
    delegation_requests: List[DelegationRequest] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DecisionDelegationManager:
    """Coordinates delegated decision actions via DelegationRequest primitives. Zero direct execution."""

    def __init__(self) -> None:
        self._plans: Dict[str, DecisionDelegationPlan] = {}

    def create_delegation_plan(
        self,
        tenant_id: str,
        decision_id: str,
        actions: List[DecisionDelegationAction],
    ) -> DecisionDelegationPlan:
        delegation_requests: List[DelegationRequest] = []

        for act in actions:
            target_enum = (
                DelegationTarget.ORCHESTRATION
                if act.target_type in ["WORKFLOW", "ORCHESTRATION"]
                else DelegationTarget.PLATFORM_OPERATIONS
            )
            req = DelegationRequest(
                tenant_id=tenant_id,
                target=target_enum,
                action=act.action_name,
                payload={"decision_id": decision_id, "target_id": act.target_id, "parameters": act.parameters},
            )
            delegation_requests.append(req)

        plan = DecisionDelegationPlan(
            tenant_id=tenant_id,
            decision_id=decision_id,
            status=DecisionDelegationStatus.DELEGATED,
            actions=actions,
            delegation_requests=delegation_requests,
        )
        self._plans[plan.delegation_plan_id] = plan
        return plan

    def get_plan(self, delegation_plan_id: str, tenant_id: str) -> DecisionDelegationPlan:
        plan = self._plans.get(delegation_plan_id)
        if not plan:
            raise ValueError(f"Delegation plan '{delegation_plan_id}' not found")
        if plan.tenant_id != tenant_id:
            raise CrossTenantDecisionGovernanceException()
        return plan
