"""Organization domain model & lifecycle management."""

import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set

from pydantic import BaseModel, Field

from app.control_plane.exceptions import OrganizationNotFoundException

logger = logging.getLogger(__name__)


class OrganizationLimits(BaseModel):
    """Resource quota allocations for an organization."""

    max_workspaces: int = 10
    max_members: int = 100
    max_agents: int = 50
    max_workflows: int = 100
    max_monthly_spend_dollars: float = 5000.0


class OrganizationSettings(BaseModel):
    """Organization-level configuration policies."""

    allow_external_sharing: bool = False
    require_mfa: bool = True
    allowed_domains: List[str] = Field(default_factory=list)
    custom_settings: Dict[str, Any] = Field(default_factory=dict)


class Organization(BaseModel):
    """Organization entity belonging to a tenant."""

    organization_id: str = Field(default_factory=lambda: f"org_{uuid.uuid4().hex[:10]}")
    tenant_id: str
    name: str
    slug: str
    limits: OrganizationLimits = Field(default_factory=OrganizationLimits)
    settings: OrganizationSettings = Field(default_factory=OrganizationSettings)
    members: Set[str] = Field(default_factory=set)  # set of user_ids
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = Field(default_factory=dict)


class OrganizationManager:
    """Manages organization creation, member access, resource limits, and settings."""

    def __init__(self) -> None:
        self._organizations: Dict[str, Organization] = {}

    def create_organization(
        self,
        name: str,
        tenant_id: str = "global",
        slug: Optional[str] = None,
        limits: Optional[OrganizationLimits] = None,
        settings: Optional[OrganizationSettings] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Organization:
        """Create a new organization within a tenant."""
        org_slug = slug or name.lower().replace(" ", "-")
        org = Organization(
            tenant_id=tenant_id,
            name=name,
            slug=org_slug,
            limits=limits or OrganizationLimits(),
            settings=settings or OrganizationSettings(),
            metadata=metadata or {},
        )
        self._organizations[org.organization_id] = org
        logger.info(f"[ORG MANAGER] Created organization '{name}' (ID: {org.organization_id}, Tenant: {tenant_id})")
        return org

    def get_organization(self, organization_id: str) -> Organization:
        """Get organization by ID."""
        org = self._organizations.get(organization_id)
        if not org:
            raise OrganizationNotFoundException(organization_id)
        return org

    def update_organization(
        self,
        organization_id: str,
        name: Optional[str] = None,
        limits: Optional[OrganizationLimits] = None,
        settings: Optional[OrganizationSettings] = None,
    ) -> Organization:
        """Update organization details, limits, or settings."""
        org = self.get_organization(organization_id)
        if name:
            org.name = name
        if limits:
            org.limits = limits
        if settings:
            org.settings = settings
        org.updated_at = datetime.now(timezone.utc)
        logger.info(f"[ORG MANAGER] Updated organization '{organization_id}'")
        return org

    def add_member(self, organization_id: str, user_id: str) -> Organization:
        """Add user to organization members."""
        org = self.get_organization(organization_id)
        if len(org.members) >= org.limits.max_members:
            raise RuntimeError(f"Organization member limit reached ({org.limits.max_members})")
        org.members.add(user_id)
        org.updated_at = datetime.now(timezone.utc)
        logger.info(f"[ORG MANAGER] Added member '{user_id}' to organization '{organization_id}'")
        return org

    def remove_member(self, organization_id: str, user_id: str) -> Organization:
        """Remove user from organization members."""
        org = self.get_organization(organization_id)
        org.members.discard(user_id)
        org.updated_at = datetime.now(timezone.utc)
        logger.info(f"[ORG MANAGER] Removed member '{user_id}' from organization '{organization_id}'")
        return org

    def delete_organization(self, organization_id: str) -> bool:
        """Delete an organization."""
        org = self.get_organization(organization_id)
        del self._organizations[organization_id]
        logger.warning(f"[ORG MANAGER] Deleted organization '{organization_id}'")
        return True

    def list_organizations(self, tenant_id: Optional[str] = None) -> List[Organization]:
        """List organizations filtered by tenant ID."""
        res = list(self._organizations.values())
        if tenant_id:
            res = [o for o in res if o.tenant_id == tenant_id]
        return res
