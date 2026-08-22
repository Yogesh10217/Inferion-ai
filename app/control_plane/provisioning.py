"""Automated Resource Provisioning Workflows for Tenants & Workspaces."""

import logging
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

from app.control_plane.tenant import TenantManager, Tenant
from app.control_plane.organization import OrganizationManager, Organization
from app.control_plane.workspace import WorkspaceManager, Workspace, WorkspaceEnvironment
from app.governance.quota_manager import QuotaManager, QuotaDefinition

logger = logging.getLogger(__name__)


class ProvisionedTenantBundle(BaseModel):
    """Complete provisioned bundle output for a new tenant."""

    tenant: Dict[str, Any]
    organization: Dict[str, Any]
    workspace: Dict[str, Any]
    quota_definition: Dict[str, Any]
    status: str = "PROVISIONED"


class ProvisioningEngine:
    """Orchestrates multi-step provisioning workflows for Tenants and Workspaces."""

    def __init__(
        self,
        tenant_manager: Optional[TenantManager] = None,
        organization_manager: Optional[OrganizationManager] = None,
        workspace_manager: Optional[WorkspaceManager] = None,
        quota_manager: Optional[QuotaManager] = None,
    ) -> None:
        self.tenant_manager = tenant_manager or TenantManager()
        self.organization_manager = organization_manager or OrganizationManager()
        self.workspace_manager = workspace_manager or WorkspaceManager()
        self.quota_manager = quota_manager or QuotaManager()

    def provision_new_tenant(
        self,
        tenant_name: str,
        org_name: Optional[str] = None,
        workspace_name: str = "Default Workspace",
        actor_id: str = "admin",
    ) -> ProvisionedTenantBundle:
        """Automated multi-step workflow provisioning Tenant -> Default Org -> Default Workspace -> Quotas."""
        logger.info(f"[PROVISIONING] Starting automated tenant provisioning for '{tenant_name}'...")

        # Step 1: Create Tenant
        tenant = self.tenant_manager.create_tenant(name=tenant_name, actor_id=actor_id)

        # Step 2: Create Primary Organization
        primary_org_name = org_name or f"{tenant_name} Org"
        org = self.organization_manager.create_organization(
            name=primary_org_name,
            tenant_id=tenant.tenant_id,
        )

        # Step 3: Create Default Workspace
        ws = self.workspace_manager.create_workspace(
            name=workspace_name,
            organization_id=org.organization_id,
            tenant_id=tenant.tenant_id,
            environment=WorkspaceEnvironment.PRODUCTION,
        )

        # Step 4: Configure Default Quotas
        quota_defn = QuotaDefinition(tenant_id=tenant.tenant_id)
        self.quota_manager.set_definition(quota_defn)

        logger.info(f"[PROVISIONING COMPLETE] Provisioned tenant bundle (Tenant ID: {tenant.tenant_id}, Org ID: {org.organization_id}, WS ID: {ws.workspace_id})")

        return ProvisionedTenantBundle(
            tenant=tenant.model_dump(),
            organization=org.model_dump(),
            workspace=ws.model_dump(),
            quota_definition=quota_defn.model_dump(),
        )

    def provision_new_workspace(
        self,
        workspace_name: str,
        organization_id: str,
        tenant_id: str,
        environment: WorkspaceEnvironment = WorkspaceEnvironment.DEVELOPMENT,
    ) -> Workspace:
        """Provision a new workspace within an existing organization."""
        org = self.organization_manager.get_organization(organization_id)
        existing = self.workspace_manager.list_workspaces(organization_id=organization_id)
        if len(existing) >= org.limits.max_workspaces:
            raise RuntimeError(f"Organization workspace limit reached ({org.limits.max_workspaces})")

        ws = self.workspace_manager.create_workspace(
            name=workspace_name,
            organization_id=organization_id,
            tenant_id=tenant_id,
            environment=environment,
        )
        logger.info(f"[PROVISIONING WORKSPACE] Provisioned workspace '{workspace_name}' (ID: {ws.workspace_id})")
        return ws
