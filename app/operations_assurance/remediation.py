"""Operational remediation planning producing DelegationRequests without direct system mutation."""

from datetime import datetime, timezone
from enum import Enum
from typing import Dict, Any, List, Optional
import uuid
from pydantic import BaseModel, Field

from app.platform_contracts.delegation import DelegationRequest, DelegationTarget, DelegationStatus
from app.operations_assurance.exceptions import OperationalRemediationBlockedException, HighRiskOperationalActionRequiresApprovalException


class RemediationPlan(BaseModel):
    remediation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    service_id: str
    action_type: str
    delegation_request: DelegationRequest
    requires_approval: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class OperationsRemediationPlanner:
    """Generates remediation delegation requests adhering strictly to Delegation-Only execution principles."""

    def __init__(self) -> None:
        pass

    def create_remediation_plan(
        self,
        tenant_id: str,
        service_id: str,
        action_type: str,
        payload: Optional[Dict[str, Any]] = None,
        target_engine: DelegationTarget = DelegationTarget.PLATFORM_OPERATIONS,
    ) -> RemediationPlan:
        # Mandatory invariant: Never directly execute. Produce a DelegationRequest.
        delegation_req = DelegationRequest(
            tenant_id=tenant_id,
            target=target_engine,
            action=action_type,
            status=DelegationStatus.CREATED,
            payload=payload or {"service_id": service_id},
        )

        return RemediationPlan(
            tenant_id=tenant_id,
            service_id=service_id,
            action_type=action_type,
            delegation_request=delegation_req,
            requires_approval=True,
        )
