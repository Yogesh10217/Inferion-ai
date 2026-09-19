"""Knowledge Assurance Delegation Module.

Enforces delegation-only execution model across knowledge systems.
"""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List

from pydantic import BaseModel, Field

from app.knowledge_assurance.exceptions import (
    CrossTenantKnowledgeAssuranceException,
    KnowledgeReferenceNotFoundException,
)
from app.platform_contracts.delegation import DelegationRequest, DelegationTarget


class KnowledgeDelegationStatus(str, Enum):
    PENDING = "PENDING"
    ISSUED = "ISSUED"
    IN_PROGRESS = "IN_PROGRESS"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    REJECTED = "REJECTED"


class KnowledgeDelegationAction(BaseModel):
    action_id: str = Field(default_factory=lambda: f"delact-{uuid.uuid4().hex[:8]}")
    target_system: str
    operation: str
    payload: Dict[str, Any] = Field(default_factory=dict)
    delegation_request_id: str = ""
    status: KnowledgeDelegationStatus = KnowledgeDelegationStatus.PENDING


class KnowledgeDelegationPlan(BaseModel):
    plan_id: str = Field(default_factory=lambda: f"delplan-{uuid.uuid4().hex[:8]}")
    tenant_id: str
    description: str
    actions: List[KnowledgeDelegationAction] = Field(default_factory=list)
    status: KnowledgeDelegationStatus = KnowledgeDelegationStatus.PENDING
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class KnowledgeDelegationManager:
    """Orchestrates knowledge delegation plans via platform DelegationRequest."""

    def __init__(self) -> None:
        self._plans: Dict[str, KnowledgeDelegationPlan] = {}
        self._requests: Dict[str, DelegationRequest] = {}

    def create_delegation_plan(
        self,
        tenant_id: str,
        description: str,
        actions_data: List[Dict[str, Any]],
    ) -> KnowledgeDelegationPlan:
        actions: List[KnowledgeDelegationAction] = []
        for item in actions_data:
            target_sys = item.get("target_system", "ORCHESTRATION")
            op = item.get("operation", "SYNC_KNOWLEDGE")
            payload = item.get("payload", {})

            del_req = DelegationRequest(
                tenant_id=tenant_id,
                target=DelegationTarget.ORCHESTRATION,
                action=op,
                payload={"target_system": target_sys, **payload},
            )
            self._requests[del_req.request_id] = del_req

            actions.append(
                KnowledgeDelegationAction(
                    target_system=target_sys,
                    operation=op,
                    payload=payload,
                    delegation_request_id=del_req.request_id,
                    status=KnowledgeDelegationStatus.ISSUED,
                )
            )

        plan = KnowledgeDelegationPlan(
            tenant_id=tenant_id,
            description=description,
            actions=actions,
            status=KnowledgeDelegationStatus.ISSUED,
        )
        self._plans[plan.plan_id] = plan
        return plan

    def get_delegation_plan(self, tenant_id: str, plan_id: str) -> KnowledgeDelegationPlan:
        if plan_id not in self._plans:
            raise KnowledgeReferenceNotFoundException(f"Delegation plan {plan_id} not found.")
        plan = self._plans[plan_id]
        if plan.tenant_id != tenant_id:
            raise CrossTenantKnowledgeAssuranceException()
        return plan

    def get_delegation_request(self, tenant_id: str, request_id: str) -> DelegationRequest:
        if request_id not in self._requests:
            raise KnowledgeReferenceNotFoundException(f"Delegation request {request_id} not found.")
        req = self._requests[request_id]
        if req.tenant_id != tenant_id:
            raise CrossTenantKnowledgeAssuranceException()
        return req

    def list_delegation_plans(self, tenant_id: str) -> List[KnowledgeDelegationPlan]:
        return [plan for plan in self._plans.values() if plan.tenant_id == tenant_id]
