"""Developer entity and lifecycle management."""

import logging
from enum import Enum
from typing import Dict, Any, Optional, List, Set
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.developer_platform.exceptions import DeveloperNotFoundException, DeveloperPermissionDeniedException

logger = logging.getLogger(__name__)


class DeveloperStatus(str, Enum):
    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    REVOKED = "REVOKED"


class DeveloperProfile(BaseModel):
    """Developer profile metadata."""

    full_name: str
    email: str
    website: Optional[str] = None
    company: Optional[str] = None
    bio: Optional[str] = None


class DeveloperOrganization(BaseModel):
    """Organization membership entry for developer."""

    organization_id: str
    tenant_id: str
    role: str = "developer"  # 'admin', 'developer', 'viewer'
    joined_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Developer(BaseModel):
    """Registered developer identity entity."""

    developer_id: str = Field(default_factory=lambda: f"dev_{uuid.uuid4().hex[:10]}")
    user_id: str
    tenant_id: str = "global"
    status: DeveloperStatus = DeveloperStatus.PENDING
    profile: DeveloperProfile
    organizations: List[DeveloperOrganization] = Field(default_factory=list)
    permissions: Set[str] = Field(default_factory=lambda: {"read", "build_extensions", "publish_marketplace"})
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    verified_at: Optional[datetime] = None
    audit_history: List[Dict[str, Any]] = Field(default_factory=list)


class DeveloperManager:
    """Manages developer registration, verification, memberships, scopes, and lifecycle."""

    def __init__(self) -> None:
        self._developers: Dict[str, Developer] = {}

    def register_developer(
        self,
        user_id: str,
        full_name: str,
        email: str,
        tenant_id: str = "global",
        company: Optional[str] = None,
        auto_activate: bool = True,
    ) -> Developer:
        """Register a new developer identity."""
        prof = DeveloperProfile(full_name=full_name, email=email, company=company)
        status = DeveloperStatus.ACTIVE if auto_activate else DeveloperStatus.PENDING
        dev = Developer(user_id=user_id, tenant_id=tenant_id, status=status, profile=prof)

        if auto_activate:
            dev.verified_at = datetime.now(timezone.utc)

        dev.audit_history.append({
            "action": "REGISTERED",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": status.value,
        })
        self._developers[dev.developer_id] = dev
        logger.info(f"[DEVELOPER MANAGER] Registered developer '{full_name}' (ID: {dev.developer_id}, Tenant: {tenant_id})")
        return dev

    def get_developer(self, developer_id: str) -> Developer:
        dev = self._developers.get(developer_id)
        if not dev:
            raise DeveloperNotFoundException(developer_id)
        return dev

    def verify_developer(self, developer_id: str) -> Developer:
        dev = self.get_developer(developer_id)
        dev.status = DeveloperStatus.ACTIVE
        dev.verified_at = datetime.now(timezone.utc)
        dev.updated_at = datetime.now(timezone.utc)
        dev.audit_history.append({
            "action": "VERIFIED",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
        return dev

    def suspend_developer(self, developer_id: str, reason: str = "Administrative action") -> Developer:
        dev = self.get_developer(developer_id)
        dev.status = DeveloperStatus.SUSPENDED
        dev.updated_at = datetime.now(timezone.utc)
        dev.audit_history.append({
            "action": "SUSPENDED",
            "reason": reason,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
        logger.warning(f"[DEVELOPER MANAGER] Suspended developer '{developer_id}': {reason}")
        return dev

    def revoke_developer(self, developer_id: str, reason: str = "Revocation") -> Developer:
        dev = self.get_developer(developer_id)
        dev.status = DeveloperStatus.REVOKED
        dev.updated_at = datetime.now(timezone.utc)
        dev.audit_history.append({
            "action": "REVOKED",
            "reason": reason,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
        logger.error(f"[DEVELOPER MANAGER] Revoked developer '{developer_id}'")
        return dev

    def validate_permission(self, developer_id: str, required_permission: str) -> bool:
        dev = self.get_developer(developer_id)
        if dev.status != DeveloperStatus.ACTIVE:
            raise DeveloperPermissionDeniedException(f"Developer '{developer_id}' is not active ({dev.status.value})")
        if required_permission not in dev.permissions:
            raise DeveloperPermissionDeniedException(f"Missing required permission '{required_permission}'")
        return True

    def list_developers(self, tenant_id: Optional[str] = None) -> List[Developer]:
        res = list(self._developers.values())
        if tenant_id:
            res = [d for d in res if d.tenant_id == tenant_id]
        return res
