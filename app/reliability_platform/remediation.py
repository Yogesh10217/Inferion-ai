"""Delegated Remediation Subsystem (Phase 5.31)."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.platform_contracts.delegation import DelegationRequest, DelegationTarget
from app.platform_contracts.idempotency import IdempotencyManager


class RemediationRisk(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class RemediationAction(BaseModel):
    action_id: str = Field(default_factory=lambda: f"act_{uuid.uuid4().hex[:12]}")
    target_manager: DelegationTarget
    action_name: str
    risk: RemediationRisk = RemediationRisk.MEDIUM
    params: Dict[str, Any] = Field(default_factory=dict)


class RemediationPlan(BaseModel):
    plan_id: str = Field(default_factory=lambda: f"plan_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    incident_id: str
    idempotency_key: str
    actions: List[RemediationAction] = Field(default_factory=list)
    delegation_request: Optional[DelegationRequest] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class RemediationManager:
    """Plans and delegates remediation execution with idempotency protection and zero direct infrastructure mutation."""

    def __init__(self, idempotency_manager: Optional[IdempotencyManager] = None) -> None:
        self.idempotency_manager = idempotency_manager or IdempotencyManager()
        self._plans: Dict[str, RemediationPlan] = {}

    def plan_remediation(
        self,
        tenant_id: str,
        incident_id: str,
        idempotency_key: str,
        actions: List[RemediationAction],
    ) -> RemediationPlan:
        # Check idempotency
        payload = {"incident_id": incident_id, "actions": [a.model_dump() for a in actions]}
        record = self.idempotency_manager.check_or_start(tenant_id, "PLAN_REMEDIATION", idempotency_key, payload)

        if record and record.result_payload:
            plan_dict = record.result_payload.get("plan")
            if plan_dict:
                return RemediationPlan(**plan_dict)

        # Create delegation request for first action
        first_action = (
            actions[0]
            if actions
            else RemediationAction(target_manager=DelegationTarget.PLATFORM_OPERATIONS, action_name="RESTART_POD")
        )
        delegation = DelegationRequest(
            tenant_id=tenant_id,
            target=first_action.target_manager,
            action=first_action.action_name,
            payload=first_action.params,
        )

        plan = RemediationPlan(
            tenant_id=tenant_id,
            incident_id=incident_id,
            idempotency_key=idempotency_key,
            actions=actions,
            delegation_request=delegation,
        )
        self._plans[plan.plan_id] = plan

        self.idempotency_manager.complete_operation(
            tenant_id=tenant_id,
            operation_type="PLAN_REMEDIATION",
            idempotency_key=idempotency_key,
            result_payload={"plan": plan.model_dump()},
        )
        return plan
