"""Tenant domain model & lifecycle management for multi-tenant isolation."""

import logging
from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.control_plane.exceptions import TenantNotFoundException, LifecycleException

logger = logging.getLogger(__name__)


class TenantStatus(str, Enum):
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    DISABLED = "DISABLED"
    PENDING = "PENDING"
    DELETED = "DELETED"


class TenantConfiguration(BaseModel):
    """Tenant-level system configuration overrides."""

    max_organizations: int = 10
    max_workspaces: int = 50
    max_concurrent_agents: int = 20
    max_tokens_per_month: int = 10000000
    allow_custom_mcp: bool = True
    enabled_providers: List[str] = Field(default_factory=lambda: ["openai", "ollama", "anthropic"])
    custom_settings: Dict[str, Any] = Field(default_factory=dict)


class TenantLifecycle(BaseModel):
    """Lifecycle history audit entry for a tenant."""

    tenant_id: str
    previous_status: Optional[TenantStatus]
    new_status: TenantStatus
    transition_reason: str
    actor_id: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Tenant(BaseModel):
    """Multi-tenant isolation unit."""

    tenant_id: str = Field(default_factory=lambda: f"tenant_{uuid.uuid4().hex[:10]}")
    name: str
    slug: str
    status: TenantStatus = TenantStatus.PENDING
    configuration: TenantConfiguration = Field(default_factory=TenantConfiguration)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    suspended_at: Optional[datetime] = None
    suspended_by: Optional[str] = None
    deleted_at: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class TenantManager:
    """Manages tenant creation, status state machine, and configuration updates."""

    def __init__(self) -> None:
        self._tenants: Dict[str, Tenant] = {}
        self._slug_index: Dict[str, str] = {}
        self._history: List[TenantLifecycle] = []

    def create_tenant(
        self,
        name: str,
        slug: Optional[str] = None,
        configuration: Optional[TenantConfiguration] = None,
        metadata: Optional[Dict[str, Any]] = None,
        actor_id: str = "system",
    ) -> Tenant:
        """Create a new tenant entity."""
        tenant_slug = slug or name.lower().replace(" ", "-")
        if tenant_slug in self._slug_index:
            raise LifecycleException(f"Tenant slug '{tenant_slug}' already exists")

        tenant = Tenant(
            name=name,
            slug=tenant_slug,
            status=TenantStatus.ACTIVE,
            configuration=configuration or TenantConfiguration(),
            metadata=metadata or {},
        )
        self._tenants[tenant.tenant_id] = tenant
        self._slug_index[tenant_slug] = tenant.tenant_id

        self._record_transition(tenant.tenant_id, None, TenantStatus.ACTIVE, "Tenant created", actor_id)
        logger.info(f"[TENANT MANAGER] Created tenant '{tenant.name}' (ID: {tenant.tenant_id})")
        return tenant

    def get_tenant(self, tenant_id: str) -> Tenant:
        """Retrieve tenant by ID."""
        tenant = self._tenants.get(tenant_id)
        if not tenant:
            raise TenantNotFoundException(tenant_id)
        return tenant

    def update_tenant(
        self,
        tenant_id: str,
        name: Optional[str] = None,
        configuration: Optional[TenantConfiguration] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Tenant:
        """Update tenant attributes or configuration."""
        tenant = self.get_tenant(tenant_id)
        if name:
            tenant.name = name
        if configuration:
            tenant.configuration = configuration
        if metadata:
            tenant.metadata.update(metadata)
        tenant.updated_at = datetime.now(timezone.utc)
        logger.info(f"[TENANT MANAGER] Updated tenant '{tenant_id}'")
        return tenant

    def suspend_tenant(self, tenant_id: str, reason: str = "Administrative action", actor_id: str = "admin") -> Tenant:
        """Suspend an active tenant."""
        tenant = self.get_tenant(tenant_id)
        if tenant.status == TenantStatus.DELETED:
            raise LifecycleException(f"Cannot suspend deleted tenant '{tenant_id}'")

        old_status = tenant.status
        tenant.status = TenantStatus.SUSPENDED
        tenant.suspended_at = datetime.now(timezone.utc)
        tenant.suspended_by = actor_id
        tenant.updated_at = datetime.now(timezone.utc)

        self._record_transition(tenant_id, old_status, TenantStatus.SUSPENDED, reason, actor_id)
        logger.warning(f"[TENANT MANAGER] Suspended tenant '{tenant_id}' (Reason: {reason})")
        return tenant

    def activate_tenant(self, tenant_id: str, actor_id: str = "admin") -> Tenant:
        """Activate a suspended or pending tenant."""
        tenant = self.get_tenant(tenant_id)
        if tenant.status == TenantStatus.DELETED:
            raise LifecycleException(f"Cannot activate deleted tenant '{tenant_id}'")

        old_status = tenant.status
        tenant.status = TenantStatus.ACTIVE
        tenant.suspended_at = None
        tenant.suspended_by = None
        tenant.updated_at = datetime.now(timezone.utc)

        self._record_transition(tenant_id, old_status, TenantStatus.ACTIVE, "Tenant activated", actor_id)
        logger.info(f"[TENANT MANAGER] Activated tenant '{tenant_id}'")
        return tenant

    def disable_tenant(self, tenant_id: str, actor_id: str = "admin") -> Tenant:
        """Disable a tenant completely."""
        tenant = self.get_tenant(tenant_id)
        old_status = tenant.status
        tenant.status = TenantStatus.DISABLED
        tenant.updated_at = datetime.now(timezone.utc)

        self._record_transition(tenant_id, old_status, TenantStatus.DISABLED, "Tenant disabled", actor_id)
        logger.warning(f"[TENANT MANAGER] Disabled tenant '{tenant_id}'")
        return tenant

    def delete_tenant(self, tenant_id: str, actor_id: str = "admin") -> Tenant:
        """Soft-delete a tenant."""
        tenant = self.get_tenant(tenant_id)
        old_status = tenant.status
        tenant.status = TenantStatus.DELETED
        tenant.deleted_at = datetime.now(timezone.utc)
        tenant.updated_at = datetime.now(timezone.utc)

        self._record_transition(tenant_id, old_status, TenantStatus.DELETED, "Tenant deleted", actor_id)
        logger.error(f"[TENANT MANAGER] Soft-deleted tenant '{tenant_id}'")
        return tenant

    def list_tenants(self, status_filter: Optional[TenantStatus] = None) -> List[Tenant]:
        """List tenant entities."""
        res = list(self._tenants.values())
        if status_filter:
            res = [t for t in res if t.status == status_filter]
        return res

    def _record_transition(
        self, tenant_id: str, old_st: Optional[TenantStatus], new_st: TenantStatus, reason: str, actor_id: str
    ) -> None:
        rec = TenantLifecycle(
            tenant_id=tenant_id,
            previous_status=old_st,
            new_status=new_st,
            transition_reason=reason,
            actor_id=actor_id,
        )
        self._history.append(rec)
