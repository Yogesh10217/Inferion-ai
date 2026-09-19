"""Control Assurance Audit Integration Subsystem (Phase 5.38)."""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

from app.control_plane.admin_audit import AdministrativeAuditLedger
from app.platform_contracts.tenant import TenantAccessGuard


class ControlAssuranceAuditEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: f"caaud_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    action: str
    target_resource_id: str
    actor_id: str = "SYSTEM"
    details: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ControlAssuranceAuditManager:
    """Manages audit logging and integration with AdministrativeAuditLedger."""

    def __init__(self, tenant_guard: Optional[TenantAccessGuard] = None) -> None:
        self.tenant_guard = tenant_guard or TenantAccessGuard()
        self.ledger = AdministrativeAuditLedger()
        self._events: Dict[str, ControlAssuranceAuditEvent] = {}

    def log_event(
        self,
        tenant_id: str,
        action: str,
        target_resource_id: str,
        actor_id: str = "SYSTEM",
        details: Optional[Dict[str, Any]] = None,
    ) -> ControlAssuranceAuditEvent:
        ev = ControlAssuranceAuditEvent(
            tenant_id=tenant_id,
            action=action,
            target_resource_id=target_resource_id,
            actor_id=actor_id,
            details=details or {},
        )
        self._events[ev.event_id] = ev

        self.ledger.record_action(
            actor_id=actor_id,
            action=action,
            target_resource_id=target_resource_id,
            tenant_id=tenant_id,
        )
        return ev
