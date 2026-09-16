"""Cross-Platform Response Planning Subsystem (Phase 5.34)."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List

from pydantic import BaseModel, Field

from app.platform_contracts.delegation import DelegationRequest, DelegationTarget


class ResponseTarget(str, Enum):
    RELIABILITY_PLATFORM = "RELIABILITY_PLATFORM"
    SECURITY_INTELLIGENCE = "SECURITY_INTELLIGENCE"
    AI_LIFECYCLE_PLATFORM = "AI_LIFECYCLE_PLATFORM"
    PLATFORM_OPERATIONS = "PLATFORM_OPERATIONS"
    APPLICATION_PLATFORM = "APPLICATION_PLATFORM"
    DEVELOPER_PLATFORM = "DEVELOPER_PLATFORM"
    ORCHESTRATION = "ORCHESTRATION"
    DECISION_INTELLIGENCE = "DECISION_INTELLIGENCE"
    PORTFOLIO_PLATFORM = "PORTFOLIO_PLATFORM"


class ResponseStatus(str, Enum):
    PLANNED = "PLANNED"
    DELEGATED = "DELEGATED"
    EXECUTING = "EXECUTING"
    COMPLETED = "COMPLETED"


class EventResponseAction(BaseModel):
    target: ResponseTarget = ResponseTarget.RELIABILITY_PLATFORM
    action_type: str = "CREATE_INCIDENT"
    payload: Dict[str, Any] = Field(default_factory=dict)


class EventResponsePlan(BaseModel):
    plan_id: str = Field(default_factory=lambda: f"resp_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    event_id: str
    actions: List[EventResponseAction] = Field(default_factory=list)
    delegation_requests: List[DelegationRequest] = Field(default_factory=list)
    status: ResponseStatus = ResponseStatus.PLANNED
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class EventResponseManager:
    """Manages delegation-only cross-platform response plans."""

    def create_response_plan(
        self,
        tenant_id: str,
        event_id: str,
        actions: List[EventResponseAction],
    ) -> EventResponsePlan:
        delegations = []
        for act in actions:
            target_enum = DelegationTarget.PLATFORM_OPERATIONS
            if act.target == ResponseTarget.ORCHESTRATION:
                target_enum = DelegationTarget.ORCHESTRATION
            elif act.target == ResponseTarget.APPLICATION_PLATFORM:
                target_enum = DelegationTarget.APPLICATION_PLATFORM

            del_req = DelegationRequest(
                tenant_id=tenant_id,
                target=target_enum,
                action=act.action_type,
                payload={"event_id": event_id, **act.payload},
            )
            delegations.append(del_req)

        return EventResponsePlan(
            tenant_id=tenant_id,
            event_id=event_id,
            actions=actions,
            delegation_requests=delegations,
            status=ResponseStatus.DELEGATED,
        )
