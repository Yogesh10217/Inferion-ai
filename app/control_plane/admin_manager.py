"""Central Administrative Manager delegating control operations across subsystems."""

import logging
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field

from app.control_plane.tenant import TenantManager
from app.control_plane.organization import OrganizationManager
from app.control_plane.workspace import WorkspaceManager

logger = logging.getLogger(__name__)


class AdminManager:
    """Master Administrative Manager coordinating Tenant, Org, Workspace, and Platform Admin capabilities."""

    def __init__(
        self,
        tenant_manager: Optional[TenantManager] = None,
        organization_manager: Optional[OrganizationManager] = None,
        workspace_manager: Optional[WorkspaceManager] = None,
    ) -> None:
        self.tenant_manager = tenant_manager or TenantManager()
        self.organization_manager = organization_manager or OrganizationManager()
        self.workspace_manager = workspace_manager or WorkspaceManager()

    def get_platform_overview(self) -> Dict[str, Any]:
        """Aggregate high-level platform administration counts."""
        tenants = self.tenant_manager.list_tenants()
        orgs = self.organization_manager.list_organizations()
        workspaces = self.workspace_manager.list_workspaces()

        return {
            "total_tenants": len(tenants),
            "active_tenants": len([t for t in tenants if t.status.value == "ACTIVE"]),
            "suspended_tenants": len([t for t in tenants if t.status.value == "SUSPENDED"]),
            "total_organizations": len(orgs),
            "total_workspaces": len(workspaces),
        }
