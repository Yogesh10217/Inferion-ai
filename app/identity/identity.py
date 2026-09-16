"""Identity Management Subsystem for Human, Service, Workload, and AI Agent Identities."""

import logging
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class IdentityType(str, Enum):
    HUMAN = "HUMAN"
    SERVICE = "SERVICE"
    AGENT = "AGENT"
    WORKLOAD = "WORKLOAD"
    API_CLIENT = "API_CLIENT"
    DEVELOPER = "DEVELOPER"
    ADMINISTRATOR = "ADMINISTRATOR"
    EXTERNAL = "EXTERNAL"


class IdentityStatus(str, Enum):
    CREATED = "CREATED"
    PENDING_VERIFICATION = "PENDING_VERIFICATION"
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    LOCKED = "LOCKED"
    COMPROMISED = "COMPROMISED"
    REVOKED = "REVOKED"
    DELETED = "DELETED"


class IdentityProfile(BaseModel):
    display_name: str = ""
    email: Optional[str] = None
    department: Optional[str] = None
    tags: List[str] = Field(default_factory=list)


class Identity(BaseModel):
    identity_id: str = Field(default_factory=lambda: f"id_{uuid.uuid4().hex[:10]}")
    username: str
    identity_type: IdentityType = IdentityType.HUMAN
    status: IdentityStatus = IdentityStatus.ACTIVE

    tenant_id: str = "global"
    organization_id: Optional[str] = None
    workspace_id: Optional[str] = None
    project_id: Optional[str] = None

    profile: IdentityProfile = Field(default_factory=IdentityProfile)
    roles: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    created_at: datetime = Field(default_factory=_now)
    last_authenticated_at: Optional[datetime] = None


class IdentityManager:
    """Manages multi-tenant identities, lifecycle state transitions, and role assignments."""

    def __init__(self) -> None:
        self._identities: Dict[str, Identity] = {}

    def create_identity(
        self,
        username: str,
        identity_type: IdentityType = IdentityType.HUMAN,
        tenant_id: str = "global",
        organization_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        roles: Optional[List[str]] = None,
        display_name: str = "",
    ) -> Identity:
        ident = Identity(
            username=username,
            identity_type=identity_type,
            tenant_id=tenant_id,
            organization_id=organization_id,
            workspace_id=workspace_id,
            roles=roles or ["viewer"],
            profile=IdentityProfile(display_name=display_name or username),
        )
        self._identities[ident.identity_id] = ident
        logger.info(f"[IDENTITY MANAGER] Registered identity '{ident.identity_id}' ({username}, {identity_type.value}) for tenant '{tenant_id}'")
        return ident

    def update_status(self, identity_id: str, new_status: IdentityStatus) -> Identity:
        ident = self.get_identity(identity_id)
        ident.status = new_status
        logger.info(f"[IDENTITY MANAGER] Identity '{identity_id}' status updated -> {new_status.value}")
        return ident

    def get_identity(self, identity_id: str) -> Identity:
        ident = self._identities.get(identity_id)
        if not ident:
            raise KeyError(f"Identity '{identity_id}' not found")
        return ident

    def list_identities(self, tenant_id: Optional[str] = None) -> List[Identity]:
        res = list(self._identities.values())
        if tenant_id:
            res = [r for r in res if r.tenant_id == tenant_id]
        return res
