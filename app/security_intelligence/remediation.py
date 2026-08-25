"""Security Remediation Planning Subsystem (Phase 5.32)."""

from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.platform_contracts.delegation import DelegationRequest, DelegationTarget
from app.platform_contracts.idempotency import IdempotencyManager
from app.security_intelligence.exceptions import SecurityRemediationBlockedException, HighRiskSecurityActionRequiresApprovalException


class SecurityRemediationStatus(str, Enum):
    PROPOSED = "PROPOSED"
    RISK_EVALUATED = "RISK_EVALUATED"
    POLICY_EVALUATED = "POLICY_EVALUATED"
    REQUIRES_APPROVAL = "REQUIRES_APPROVAL"
    APPROVED = "APPROVED"
    DELEGATED = "DELEGATED"
    EXECUTING = "EXECUTING"
    VERIFIED = "VERIFIED"


class SecurityRemediationPriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class SecurityRemediationAction(BaseModel):
    action_id: str = Field(default_factory=lambda: f"sact_{uuid.uuid4().hex[:12]}")
    target_manager: DelegationTarget
    action_name: str
    priority: SecurityRemediationPriority = SecurityRemediationPriority.MEDIUM
    params: Dict[str, Any] = Field(default_factory=dict)


class SecurityRemediationPlan(BaseModel):
    plan_id: str = Field(default_factory=lambda: f"splan_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    incident_id: str
    idempotency_key: str
    priority: SecurityRemediationPriority = SecurityRemediationPriority.HIGH
    actions: List[SecurityRemediationAction] = Field(default_factory=list)
    status: SecurityRemediationStatus = SecurityRemediationStatus.PROPOSED
    delegation_request: Optional[DelegationRequest] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class SecurityRemediationManager:
    """Plans security remediations delegating execution strictly via DelegationRequest and IdempotencyManager."""

    def __init__(self, idempotency_manager: Optional[IdempotencyManager] = None) -> None:
        self.idempotency_manager = idempotency_manager or IdempotencyManager()
        self._plans: Dict[str, SecurityRemediationPlan] = {}

    def plan_remediation(
        self,
        tenant_id: str,
        incident_id: str,
        idempotency_key: str,
        actions: List[SecurityRemediationAction],
        priority: SecurityRemediationPriority = SecurityRemediationPriority.HIGH,
    ) -> SecurityRemediationPlan:
        payload = {"incident_id": incident_id, "actions": [a.model_dump() for a in actions]}
        record = self.idempotency_manager.check_or_start(tenant_id, "PLAN_SECURITY_REMEDIATION", idempotency_key, payload)

        if record and record.result_payload:
            plan_dict = record.result_payload.get("plan")
            if plan_dict:
                return SecurityRemediationPlan(**plan_dict)

        first_action = actions[0] if actions else SecurityRemediationAction(target_manager=DelegationTarget.PLATFORM_OPERATIONS, action_name="REVOKE_KEY")

        delegation = DelegationRequest(
            tenant_id=tenant_id,
            target=first_action.target_manager,
            action=first_action.action_name,
            payload=first_action.params,
        )

        plan = SecurityRemediationPlan(
            tenant_id=tenant_id,
            incident_id=incident_id,
            idempotency_key=idempotency_key,
            priority=priority,
            actions=actions,
            delegation_request=delegation,
        )
        self._plans[plan.plan_id] = plan

        self.idempotency_manager.complete_operation(
            tenant_id=tenant_id,
            operation_type="PLAN_SECURITY_REMEDIATION",
            idempotency_key=idempotency_key,
            result_payload={"plan": plan.model_dump()},
        )
        return plan
