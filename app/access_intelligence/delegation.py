"""Delegated Access Action Coordination (Phase 5.39)."""

from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.access_intelligence.exceptions import CrossTenantAccessIntelligenceException
from app.platform_contracts.delegation import DelegationRequest, DelegationTarget, DelegationStatus


class AccessDelegationAction(str, Enum):
    REVOKE_IAM_ROLE = "REVOKE_IAM_ROLE"
    EXPIRE_TEMPORARY_CREDENTIAL = "EXPIRE_TEMPORARY_CREDENTIAL"
    DISABLE_SERVICE_IDENTITY = "DISABLE_SERVICE_IDENTITY"
    REDUCE_AGENT_TOOL_SCOPE = "REDUCE_AGENT_TOOL_SCOPE"
    TRIGGER_ACCESS_RECERTIFICATION = "TRIGGER_ACCESS_RECERTIFICATION"


class AccessDelegationStatus(str, Enum):
    INITIALIZED = "INITIALIZED"
    DELEGATED = "DELEGATED"
    EXECUTED = "EXECUTED"
    FAILED = "FAILED"


class AccessDelegationPlan(BaseModel):
    """Delegated Access Plan representation."""
    delegation_plan_id: str = Field(default_factory=lambda: f"del_plan_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    action: AccessDelegationAction
    target_identity_id: str
    delegation_request: DelegationRequest
    status: AccessDelegationStatus = AccessDelegationStatus.INITIALIZED
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AccessDelegationManager:
    """Coordinates delegated actions without mutating external IAM directly."""

    def __init__(self) -> None:
        self._plans: Dict[str, AccessDelegationPlan] = {}

    def create_delegation_plan(
        self,
        tenant_id: str,
        action: AccessDelegationAction,
        target_identity_id: str,
        payload: Optional[Dict[str, Any]] = None,
    ) -> AccessDelegationPlan:
        del_req = DelegationRequest(
            tenant_id=tenant_id,
            target=DelegationTarget.PLATFORM_OPERATIONS,
            action=action.value,
            status=DelegationStatus.QUEUED,
            payload=payload or {"target_identity_id": target_identity_id},
        )
        plan = AccessDelegationPlan(
            tenant_id=tenant_id,
            action=action,
            target_identity_id=target_identity_id,
            delegation_request=del_req,
            status=AccessDelegationStatus.DELEGATED,
        )
        self._plans[plan.delegation_plan_id] = plan
        return plan

    def get_delegation_plan(self, tenant_id: str, delegation_plan_id: str) -> AccessDelegationPlan:
        plan = self._plans.get(delegation_plan_id)
        if not plan or plan.tenant_id != tenant_id:
            raise CrossTenantAccessIntelligenceException()
        return plan

    def list_delegation_plans(self, tenant_id: str) -> List[AccessDelegationPlan]:
        return [p for p in self._plans.values() if p.tenant_id == tenant_id]
