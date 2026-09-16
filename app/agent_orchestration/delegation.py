"""Delegation Subsystem Integrating Platform Contracts (Phase 5.36)."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.agent_orchestration.exceptions import AgentDelegationBlockedException, CrossTenantAgentAccessException
from app.platform_contracts.delegation import (
    DelegationRequest,
    DelegationResult,
    DelegationStatus,
    DelegationTarget,
)
from app.platform_contracts.tenant import TenantAccessGuard


class AgentDelegationStatus(str, Enum):
    CREATED = "CREATED"
    QUEUED = "QUEUED"
    DELEGATED = "DELEGATED"
    EXECUTING = "EXECUTING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class AgentDelegationAction(BaseModel):
    action_name: str
    target_system: DelegationTarget = DelegationTarget.PLATFORM_OPERATIONS
    payload: Dict[str, Any] = Field(default_factory=dict)


class AgentDelegationPlan(BaseModel):
    delegation_plan_id: str = Field(default_factory=lambda: f"delplan_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    agent_id: str
    task_id: str
    requests: List[DelegationRequest] = Field(default_factory=list)
    status: DelegationStatus = DelegationStatus.CREATED
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AgentDelegationManager:
    """Creates and tracks governed DelegationRequest objects targeting existing platform subsystems."""

    def __init__(self, tenant_guard: Optional[TenantAccessGuard] = None) -> None:
        self.tenant_guard = tenant_guard or TenantAccessGuard()
        self._delegations: Dict[str, DelegationRequest] = {}
        self._plans: Dict[str, AgentDelegationPlan] = {}

    def create_delegation_request(
        self,
        tenant_id: str,
        target: DelegationTarget,
        action: str,
        payload: Optional[Dict[str, Any]] = None,
        delegation_id: Optional[str] = None,
    ) -> DelegationRequest:
        did = delegation_id or f"delreq_{uuid.uuid4().hex[:12]}"
        req = DelegationRequest(
            delegation_id=did,
            tenant_id=tenant_id,
            target=target,
            action=action,
            payload=payload or {},
            status=DelegationStatus.CREATED,
        )
        self._delegations[req.delegation_id] = req
        return req

    def get_delegation_request(self, delegation_id: str, tenant_id: str) -> DelegationRequest:
        req = self._delegations.get(delegation_id)
        if not req:
            raise AgentDelegationBlockedException(f"Delegation request '{delegation_id}' not found.")

        try:
            self.tenant_guard.enforce_isolation(tenant_id, req.tenant_id)
        except Exception:
            raise CrossTenantAgentAccessException(tenant_id, req.tenant_id)

        return req

    def simulate_delegated_execution(self, delegation_id: str, tenant_id: str) -> DelegationResult:
        req = self.get_delegation_request(delegation_id, tenant_id)
        req.status = DelegationStatus.COMPLETED
        return DelegationResult(
            delegation_id=req.delegation_id,
            status=DelegationStatus.COMPLETED,
            target_reference_id=f"target_ref_{uuid.uuid4().hex[:8]}",
            output={"result": "Delegated execution successfully handled by existing platform manager.", "action": req.action},
        )
