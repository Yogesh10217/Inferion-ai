"""Administrative Audit Ledger with Automatic Secret Redaction."""

import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.security.secrets import SecretManager

logger = logging.getLogger(__name__)


class AdministrativeAuditEvent(BaseModel):
    """Immutable audit record for control plane mutations."""

    audit_id: str = Field(default_factory=lambda: f"audit_{uuid.uuid4().hex[:12]}")
    actor_id: str
    tenant_id: str = "global"
    organization_id: Optional[str] = None
    workspace_id: Optional[str] = None
    action: str
    target_resource_id: str
    previous_state: Optional[Dict[str, Any]] = None
    new_state: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    request_id: Optional[str] = None
    trace_id: Optional[str] = None
    approval_id: Optional[str] = None


class AdministrativeAuditLedger:
    """Records every administrative mutation with guaranteed secret redaction."""

    def __init__(self, secret_manager: Optional[SecretManager] = None) -> None:
        self.secret_manager = secret_manager or SecretManager()
        self._audit_records: List[AdministrativeAuditEvent] = []

    def record_action(
        self,
        actor_id: str,
        action: str,
        target_resource_id: str,
        tenant_id: str = "global",
        organization_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        previous_state: Optional[Dict[str, Any]] = None,
        new_state: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None,
        trace_id: Optional[str] = None,
        approval_id: Optional[str] = None,
    ) -> AdministrativeAuditEvent:
        """Record administrative action into sanitized audit ledger."""
        # Sanitize states
        prev_sanitized = self._sanitize_dict(previous_state) if previous_state else None
        new_sanitized = self._sanitize_dict(new_state) if new_state else None

        event = AdministrativeAuditEvent(
            actor_id=actor_id,
            tenant_id=tenant_id,
            organization_id=organization_id,
            workspace_id=workspace_id,
            action=action,
            target_resource_id=target_resource_id,
            previous_state=prev_sanitized,
            new_state=new_sanitized,
            request_id=request_id,
            trace_id=trace_id,
            approval_id=approval_id,
        )
        self._audit_records.append(event)
        logger.info(f"[ADMIN AUDIT] Action '{action}' by '{actor_id}' on target '{target_resource_id}' (Tenant: {tenant_id})")
        return event

    def _sanitize_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Redact sensitive fields from state dictionary."""
        sanitized = {}
        for k, v in data.items():
            if isinstance(v, str):
                sanitized[k] = self.secret_manager.sanitize_text(v)
            elif isinstance(v, dict):
                sanitized[k] = self._sanitize_dict(v)
            else:
                sanitized[k] = v
        return sanitized

    def list_records(self, tenant_id: Optional[str] = None, actor_id: Optional[str] = None) -> List[AdministrativeAuditEvent]:
        res = list(self._audit_records)
        if tenant_id:
            res = [r for r in res if r.tenant_id in (tenant_id, "global")]
        if actor_id:
            res = [r for r in res if r.actor_id == actor_id]
        return res
