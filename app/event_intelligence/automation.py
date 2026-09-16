"""Governance-Aware Automation Planning Subsystem (Phase 5.34)."""

import uuid
from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, Field

from app.event_intelligence.events import EnterpriseEvent
from app.platform_contracts.delegation import DelegationRequest, DelegationTarget


class AutomationAction(str, Enum):
    CREATE_INCIDENT = "CREATE_INCIDENT"
    REQUEST_INVESTIGATION = "REQUEST_INVESTIGATION"
    REQUEST_SECURITY_REMEDIATION = "REQUEST_SECURITY_REMEDIATION"
    REQUEST_ROLLBACK = "REQUEST_ROLLBACK"
    REQUEST_DECISION = "REQUEST_DECISION"
    REQUEST_APPROVAL = "REQUEST_APPROVAL"
    TRIGGER_ORCHESTRATION = "TRIGGER_ORCHESTRATION"
    NOTIFY_HUMAN_TASK = "NOTIFY_HUMAN_TASK"
    GENERATE_REPORT = "GENERATE_REPORT"


class AutomationStatus(str, Enum):
    PLANNED = "PLANNED"
    DELEGATED = "DELEGATED"
    REQUIRE_APPROVAL = "REQUIRE_APPROVAL"
    BLOCKED = "BLOCKED"
    COMPLETED = "COMPLETED"


class AutomationEligibility(BaseModel):
    is_eligible: bool = True
    reason: str = "Eligible for automated response"


class AutomationTrigger(BaseModel):
    event_type: str
    min_severity: str = "MEDIUM"


class AutomationCondition(BaseModel):
    condition_name: str
    value: str


class AutomationPlan(BaseModel):
    plan_id: str = Field(default_factory=lambda: f"autoplan_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    event_id: str
    action: AutomationAction = AutomationAction.REQUEST_INVESTIGATION
    status: AutomationStatus = AutomationStatus.PLANNED
    delegation_request: DelegationRequest
    requires_approval: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AutomationManager:
    """Plans governance-aware automations delegating execution strictly via DelegationRequest."""

    def create_automation_plan(
        self,
        event: EnterpriseEvent,
        action: AutomationAction = AutomationAction.REQUEST_INVESTIGATION,
        requires_approval: bool = False,
        delegation_target: DelegationTarget = DelegationTarget.PLATFORM_OPERATIONS,
    ) -> AutomationPlan:
        delegation = DelegationRequest(
            tenant_id=event.tenant_id,
            target=delegation_target,
            action=action.value,
            payload={"event_id": event.event_id, "event_type": event.event_type.value},
        )
        plan_status = AutomationStatus.REQUIRE_APPROVAL if requires_approval else AutomationStatus.DELEGATED

        return AutomationPlan(
            tenant_id=event.tenant_id,
            event_id=event.event_id,
            action=action,
            status=plan_status,
            delegation_request=delegation,
            requires_approval=requires_approval,
        )
