"""Identity Audit Lineage & Access Log Subsystem."""

import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.control_plane.admin_audit import AdministrativeAuditLedger

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class IdentityAuditEvent(BaseModel):
    audit_id: str = Field(default_factory=lambda: f"id_aud_{uuid.uuid4().hex[:10]}")
    event_type: str  # AUTHENTICATION, AUTHORIZATION, PRIVILEGED_ACCESS, TOKEN_ROTATION, REVOCATION
    identity_id: str
    tenant_id: str = "global"

    action: str
    resource_id: str
    outcome: str
    context: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=_now)


class IdentityAuditManager:
    """Manages identity access lineage logging and integrates with AdministrativeAuditLedger."""

    def __init__(self, admin_audit_ledger: Optional[AdministrativeAuditLedger] = None) -> None:
        self.admin_audit_ledger = admin_audit_ledger or AdministrativeAuditLedger()
        self._audit_events: List[IdentityAuditEvent] = []

    def record_event(
        self,
        event_type: str,
        identity_id: str,
        action: str,
        resource_id: str,
        outcome: str,
        tenant_id: str = "global",
        context: Optional[Dict[str, Any]] = None,
    ) -> IdentityAuditEvent:
        evt = IdentityAuditEvent(
            event_type=event_type,
            identity_id=identity_id,
            tenant_id=tenant_id,
            action=action,
            resource_id=resource_id,
            outcome=outcome,
            context=context or {},
        )
        self._audit_events.append(evt)

        # Log on AdministrativeAuditLedger
        if hasattr(self.admin_audit_ledger, "record_entry"):
            try:
                self.admin_audit_ledger.record_entry(
                    action=f"IDENTITY_{event_type}",
                    actor=identity_id,
                    target=resource_id,
                    details={"outcome": outcome, "tenant_id": tenant_id},
                )
            except Exception:  # nosec B110
                pass

        logger.info(
            f"[IDENTITY AUDIT] Recorded {event_type} for '{identity_id}' on '{resource_id}': Outcome = {outcome}"
        )
        return evt

    def list_events(
        self, tenant_id: Optional[str] = None, identity_id: Optional[str] = None
    ) -> List[IdentityAuditEvent]:
        res = list(self._audit_events)
        if tenant_id:
            res = [r for r in res if r.tenant_id == tenant_id]
        if identity_id:
            res = [r for r in res if r.identity_id == identity_id]
        return res
