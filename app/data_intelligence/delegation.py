"""Delegated data action coordination (Phase 5.43)."""

import uuid
from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from pydantic import BaseModel, Field

from app.data_intelligence.exceptions import CrossTenantDataIntelligenceException
from app.platform_contracts.delegation import DelegationRequest


class DataDelegationStatus(str, Enum):
    PENDING = "PENDING"
    SUBMITTED = "SUBMITTED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class DataDelegationAction(BaseModel):
    action_id: str
    target_subsystem: str
    action_name: str
    params: Dict[str, Any] = Field(default_factory=dict)


class DataDelegationPlan(BaseModel):
    plan_id: str
    tenant_id: str
    actions: List[DataDelegationAction] = Field(default_factory=list)
    delegation_requests: List[DelegationRequest] = Field(default_factory=list)
    status: DataDelegationStatus = DataDelegationStatus.PENDING
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DataDelegationManager:
    """Coordinates creation of DelegationRequest objects for all external data actions."""

    def __init__(self) -> None:
        self._plans: Dict[str, DataDelegationPlan] = {}

    def create_delegation_plan(
        self,
        tenant_id: str,
        actions: List[DataDelegationAction],
        plan_id: Optional[str] = None,
    ) -> DataDelegationPlan:
        pid = plan_id or f"ddel-{uuid.uuid4().hex[:8]}"

        del_reqs = []
        for a in actions:
            target_name = a.target_subsystem.upper()
            if target_name not in ("PLATFORM_OPERATIONS", "APPLICATION_PLATFORM", "DEVELOPER_PLATFORM", "ORCHESTRATION", "INTEGRATION", "ARCHITECTURE_PLATFORM", "PORTFOLIO_PLATFORM"):
                target_name = "ORCHESTRATION"
            del_reqs.append(
                DelegationRequest(
                    delegation_id=f"del-req-{uuid.uuid4().hex[:8]}",
                    tenant_id=tenant_id,
                    target=target_name,
                    action=a.action_name,
                    payload=a.params,
                )
            )

        plan = DataDelegationPlan(
            plan_id=pid,
            tenant_id=tenant_id,
            actions=actions,
            delegation_requests=del_reqs,
            status=DataDelegationStatus.SUBMITTED,
        )
        self._plans[pid] = plan
        return plan

    def get_plan(self, plan_id: str, tenant_id: str) -> DataDelegationPlan:
        p = self._plans.get(plan_id)
        if not p:
            raise Exception(f"Delegation plan '{plan_id}' not found.")
        if p.tenant_id != tenant_id:
            raise CrossTenantDataIntelligenceException()
        return p
