"""Standardized Audit Event Contract (Phase 5.30)."""

from enum import Enum
from typing import Dict, Any, Optional
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.control_plane.admin_audit import AdministrativeAuditLedger


class AuditEventType(str, Enum):
    RESOURCE_CREATED = "RESOURCE_CREATED"
    RESOURCE_UPDATED = "RESOURCE_UPDATED"
    RESOURCE_FINALIZED = "RESOURCE_FINALIZED"
    RESOURCE_DELETED = "RESOURCE_DELETED"
    ACCESS_DENIED = "ACCESS_DENIED"
    GOVERNANCE_EVALUATED = "GOVERNANCE_EVALUATED"


class AuditActorReference(BaseModel):
    principal_id: str
    tenant_id: str
    roles: list[str] = Field(default_factory=list)


class AuditResourceReference(BaseModel):
    resource_type: str
    resource_id: str
    tenant_id: str


class PlatformAuditEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: f"aud_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    event_type: AuditEventType = AuditEventType.RESOURCE_FINALIZED
    resource: AuditResourceReference
    actor: AuditActorReference
    previous_fingerprint: Optional[str] = None
    new_fingerprint: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AuditReference(BaseModel):
    audit_event_id: str
    tenant_id: str
