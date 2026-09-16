"""Governed Data Usage Tracking & Audit Logging Subsystem."""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.data_governance.access import DataAction, PrincipalType


class DataUsageEvent(BaseModel):
    """Immutable record of governed data access or operation."""

    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    principal_id: str
    principal_type: PrincipalType
    asset_id: str
    purpose: str
    action: DataAction
    authorization_decision: str
    decision_id: Optional[str] = None
    correlation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = Field(default_factory=dict)  # Crucial: Payload content excluded


class DataUsageManager:
    """Audits and tracks data asset usage across users, agents, workflows, models, and applications."""

    def __init__(self) -> None:
        self._events: Dict[str, List[DataUsageEvent]] = {}  # tenant_id -> list

    def log_usage_event(
        self,
        tenant_id: str,
        principal_id: str,
        principal_type: PrincipalType,
        asset_id: str,
        purpose: str,
        action: DataAction,
        authorization_decision: str,
        decision_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> DataUsageEvent:
        event = DataUsageEvent(
            tenant_id=tenant_id,
            principal_id=principal_id,
            principal_type=principal_type,
            asset_id=asset_id,
            purpose=purpose,
            action=action,
            authorization_decision=authorization_decision,
            decision_id=decision_id,
            metadata=metadata or {},
        )
        if tenant_id not in self._events:
            self._events[tenant_id] = []
        self._events[tenant_id].append(event)
        return event

    def list_usage_events(
        self,
        tenant_id: str,
        asset_id: Optional[str] = None,
        principal_id: Optional[str] = None,
        limit: int = 100,
    ) -> List[DataUsageEvent]:
        events = self._events.get(tenant_id, [])
        if asset_id:
            events = [e for e in events if e.asset_id == asset_id]
        if principal_id:
            events = [e for e in events if e.principal_id == principal_id]
        return events[-limit:]
