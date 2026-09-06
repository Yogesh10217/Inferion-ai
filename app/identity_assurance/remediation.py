"""Identity Remediation Planning."""

from datetime import datetime, timezone
from enum import Enum
from typing import Dict, Any, List, Optional
import uuid
from pydantic import BaseModel, Field

from app.identity_assurance.exceptions import CrossTenantIdentityAssuranceException
from app.platform_contracts.delegation import DelegationRequest, DelegationTarget


class IdentityRemediationPriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class IdentityRemediationStatus(str, Enum):
    PLANNED = "PLANNED"
    SUBMITTED = "SUBMITTED"
    EXECUTED = "EXECUTED"
    VERIFIED = "VERIFIED"


class IdentityRemediationAction(BaseModel):
    action_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    action_type: str  # REVOKE_UNUSED_ROLE, ENABLE_MFA, ROTATE_STALE_KEY, REMOVE_TOXIC_PERM
    target_identity_id: str
    priority: IdentityRemediationPriority = IdentityRemediationPriority.MEDIUM
    description: str = ""


class IdentityRemediationPlan(BaseModel):
    plan_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    identity_id: str
    actions: List[IdentityRemediationAction] = Field(default_factory=list)
    status: IdentityRemediationStatus = IdentityRemediationStatus.PLANNED
    delegation_requests: List[DelegationRequest] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class IdentityRemediationManager:
    """Manages identity remediation plans producing DelegationRequests (zero direct IAM mutations)."""

    def __init__(self) -> None:
        self._plans: Dict[str, IdentityRemediationPlan] = {}

    def plan_remediation(
        self,
        tenant_id: str,
        identity_id: str,
        actions: List[IdentityRemediationAction],
    ) -> IdentityRemediationPlan:
        requests = []
        for action in actions:
            req = DelegationRequest(
                tenant_id=tenant_id,
                target=DelegationTarget.APPLICATION_PLATFORM,
                action=action.action_type,
                payload={
                    "identity_id": identity_id,
                    "priority": action.priority.value,
                    "description": action.description,
                },
            )
            requests.append(req)

        plan = IdentityRemediationPlan(
            tenant_id=tenant_id,
            identity_id=identity_id,
            actions=actions,
            status=IdentityRemediationStatus.SUBMITTED,
            delegation_requests=requests,
        )
        self._plans[plan.plan_id] = plan
        return plan

    def get_plan(self, tenant_id: str, plan_id: str) -> IdentityRemediationPlan:
        plan = self._plans.get(plan_id)
        if not plan or plan.tenant_id != tenant_id:
            raise CrossTenantIdentityAssuranceException()
        return plan
