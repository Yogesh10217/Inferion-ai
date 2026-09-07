"""Security Delegation Manager (Delegation-Only Execution Invariant)."""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.platform_contracts.delegation import DelegationRequest, DelegationTarget

logger = logging.getLogger(__name__)


class SecurityDelegationAction(BaseModel):
    action_id: str = Field(default_factory=lambda: f"del-act-{uuid.uuid4().hex[:8]}")
    target_system: str  # SIEM, SOAR, FIREWALL, IAM
    action_name: str
    parameters: Dict[str, Any] = Field(default_factory=dict)


class SecurityDelegationPlan(BaseModel):
    delegation_id: str = Field(default_factory=lambda: f"sec-del-{uuid.uuid4().hex[:8]}")
    tenant_id: str
    target_system: str
    actions: List[SecurityDelegationAction]
    delegation_request_id: str
    status: str = "DELEGATED"
    idempotency_key: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class SecurityDelegationManager:
    """Manages delegation of security mutations to external execution engines without performing direct mutations."""

    def __init__(self) -> None:
        self._delegations: Dict[str, SecurityDelegationPlan] = {}
        self._idempotency_map: Dict[str, str] = {}

    def delegate_action(
        self,
        tenant_id: str,
        target_system: str,
        action_name: str,
        parameters: Optional[Dict[str, Any]] = None,
        idempotency_key: Optional[str] = None,
    ) -> SecurityDelegationPlan:
        if idempotency_key and idempotency_key in self._idempotency_map:
            existing_id = self._idempotency_map[idempotency_key]
            return self._delegations[existing_id]

        act = SecurityDelegationAction(
            target_system=target_system,
            action_name=action_name,
            parameters=parameters or {},
        )

        del_req = DelegationRequest(
            tenant_id=tenant_id,
            target=DelegationTarget.PLATFORM_OPERATIONS,
            action=action_name,
            payload=parameters or {},
        )

        plan = SecurityDelegationPlan(
            tenant_id=tenant_id,
            target_system=target_system,
            actions=[act],
            delegation_request_id=del_req.request_id,
            idempotency_key=idempotency_key,
        )

        self._delegations[plan.delegation_id] = plan
        if idempotency_key:
            self._idempotency_map[idempotency_key] = plan.delegation_id

        logger.info(f"[SECURITY DELEGATION] Delegated action '{action_name}' to system '{target_system}' (Request ID: {del_req.request_id})")
        return plan

    def list_delegations(self, tenant_id: str) -> List[SecurityDelegationPlan]:
        return [d for d in self._delegations.values() if d.tenant_id == tenant_id]
