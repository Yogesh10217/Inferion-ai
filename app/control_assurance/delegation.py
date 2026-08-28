"""Delegated Remediation Coordination Subsystem (Phase 5.38)."""

from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.platform_contracts.tenant import TenantAccessGuard
from app.platform_contracts.delegation import DelegationRequest, DelegationTarget
from app.control_assurance.exceptions import (
    ControlRemediationBlockedException,
    CrossTenantControlAssuranceAccessException,
)


class ControlDelegationStatus(str, Enum):
    PLANNED = "PLANNED"
    DELEGATED = "DELEGATED"
    COMPLETED = "COMPLETED"
    BLOCKED = "BLOCKED"


class ControlDelegationAction(BaseModel):
    action_type: str
    target_system: DelegationTarget = DelegationTarget.PLATFORM_OPERATIONS
    parameters: Dict[str, Any] = Field(default_factory=dict)


class ControlDelegationPlan(BaseModel):
    plan_id: str = Field(default_factory=lambda: f"delplan_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    control_id: str
    status: ControlDelegationStatus = ControlDelegationStatus.PLANNED
    delegation_id: Optional[str] = None
    action: ControlDelegationAction


class ControlDelegationManager:
    """Coordinates remediation via DelegationRequest with zero direct mutation."""

    def __init__(self, tenant_guard: Optional[TenantAccessGuard] = None) -> None:
        self.tenant_guard = tenant_guard or TenantAccessGuard()
        self._plans: Dict[str, ControlDelegationPlan] = {}

    def delegate_action(
        self,
        tenant_id: str,
        control_id: str,
        action_type: str,
        target_system: DelegationTarget = DelegationTarget.PLATFORM_OPERATIONS,
        parameters: Optional[Dict[str, Any]] = None,
        direct_mutation_attempted: bool = False,
    ) -> ControlDelegationPlan:
        if direct_mutation_attempted:
            raise ControlRemediationBlockedException(
                "direct_mutation", "Direct mutation is strictly prohibited. All actions must use DelegationRequest."
            )

        delegation = DelegationRequest(
            tenant_id=tenant_id,
            target=target_system,
            action=action_type,
            payload=parameters or {},
        )

        plan = ControlDelegationPlan(
            tenant_id=tenant_id,
            control_id=control_id,
            status=ControlDelegationStatus.DELEGATED,
            delegation_id=delegation.delegation_id,
            action=ControlDelegationAction(
                action_type=action_type,
                target_system=target_system,
                parameters=parameters or {},
            ),
        )
        self._plans[plan.plan_id] = plan
        return plan
