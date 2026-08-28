"""Control Remediation Planning Subsystem (Phase 5.38)."""

from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.platform_contracts.tenant import TenantAccessGuard
from app.platform_contracts.idempotency import IdempotencyManager
from app.platform_contracts.delegation import DelegationRequest, DelegationTarget
from app.control_assurance.exceptions import (
    ControlRemediationBlockedException,
    CrossTenantControlAssuranceAccessException,
)


class RemediationPriority(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class RemediationStatus(str, Enum):
    PLANNED = "PLANNED"
    DELEGATED = "DELEGATED"
    VERIFYING = "VERIFYING"
    RESOLVED = "RESOLVED"
    FAILED = "FAILED"


class ControlRemediationAction(BaseModel):
    action_id: str = Field(default_factory=lambda: f"act_{uuid.uuid4().hex[:12]}")
    action_type: str
    target_component: str
    parameters: Dict[str, Any] = Field(default_factory=dict)


class ControlRemediationPlan(BaseModel):
    plan_id: str = Field(default_factory=lambda: f"cplan_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    violation_id: str
    control_id: str
    priority: RemediationPriority = RemediationPriority.HIGH
    status: RemediationStatus = RemediationStatus.PLANNED
    actions: List[ControlRemediationAction] = Field(default_factory=list)
    delegation_id: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ControlRemediationManager:
    """Manages control remediation plans, emitting DelegationRequest with zero direct mutation."""

    def __init__(self, tenant_guard: Optional[TenantAccessGuard] = None) -> None:
        self.tenant_guard = tenant_guard or TenantAccessGuard()
        self.idempotency_manager = IdempotencyManager()
        self._plans: Dict[str, ControlRemediationPlan] = {}

    def plan_remediation(
        self,
        tenant_id: str,
        violation_id: str,
        control_id: str,
        actions: Optional[List[ControlRemediationAction]] = None,
        idempotency_key: str = "default_key",
    ) -> ControlRemediationPlan:
        # Idempotency check
        existing = self.idempotency_manager.check_or_start(
            tenant_id=tenant_id,
            operation_type="plan_remediation",
            idempotency_key=idempotency_key,
            request_payload={"violation_id": violation_id, "control_id": control_id},
        )
        if existing and existing.result_payload and "plan_id" in existing.result_payload:
            plan_id = existing.result_payload["plan_id"]
            if plan_id in self._plans:
                return self._plans[plan_id]

        plan = ControlRemediationPlan(
            tenant_id=tenant_id,
            violation_id=violation_id,
            control_id=control_id,
            priority=RemediationPriority.HIGH,
            actions=actions or [],
        )

        # Delegate execution
        delegation = DelegationRequest(
            tenant_id=tenant_id,
            target=DelegationTarget.PLATFORM_OPERATIONS,
            action="REMEDIATE_CONTROL",
            payload={"plan_id": plan.plan_id, "control_id": control_id},
        )
        plan.delegation_id = delegation.delegation_id
        plan.status = RemediationStatus.DELEGATED

        self._plans[plan.plan_id] = plan
        self.idempotency_manager.complete_operation(
            tenant_id=tenant_id,
            operation_type="plan_remediation",
            idempotency_key=idempotency_key,
            result_payload={"plan_id": plan.plan_id},
        )
        return plan
