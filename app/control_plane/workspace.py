"""Workspace domain model & environment isolation management."""

import logging
from enum import Enum
from typing import Dict, Any, Optional, List, Set
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.control_plane.exceptions import WorkspaceNotFoundException

logger = logging.getLogger(__name__)


class WorkspaceEnvironment(str, Enum):
    DEVELOPMENT = "DEVELOPMENT"
    STAGING = "STAGING"
    PRODUCTION = "PRODUCTION"
    SANDBOX = "SANDBOX"


class WorkspaceLimits(BaseModel):
    """Resource limits scoped to a workspace."""

    max_agents: int = 10
    max_workflows: int = 20
    max_tools: int = 50
    max_concurrent_executions: int = 5


class WorkspaceSettings(BaseModel):
    """Workspace-level operational flags."""

    auto_approval_enabled: bool = False
    debug_mode: bool = False
    allowed_models: List[str] = Field(default_factory=list)
    custom_settings: Dict[str, Any] = Field(default_factory=dict)


class Workspace(BaseModel):
    """Workspace isolation entity belonging to an Organization and Tenant."""

    workspace_id: str = Field(default_factory=lambda: f"ws_{uuid.uuid4().hex[:10]}")
    organization_id: str
    tenant_id: str
    name: str
    environment: WorkspaceEnvironment = WorkspaceEnvironment.DEVELOPMENT
    limits: WorkspaceLimits = Field(default_factory=WorkspaceLimits)
    settings: WorkspaceSettings = Field(default_factory=WorkspaceSettings)
    members: Set[str] = Field(default_factory=set)
    is_archived: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    archived_at: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class WorkspaceManager:
    """Manages workspace creation, environment isolation, archiving, and member access."""

    def __init__(self) -> None:
        self._workspaces: Dict[str, Workspace] = {}

    def create_workspace(
        self,
        name: str,
        organization_id: str,
        tenant_id: str = "global",
        environment: WorkspaceEnvironment = WorkspaceEnvironment.DEVELOPMENT,
        limits: Optional[WorkspaceLimits] = None,
        settings: Optional[WorkspaceSettings] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Workspace:
        """Create a new workspace within an organization."""
        ws = Workspace(
            organization_id=organization_id,
            tenant_id=tenant_id,
            name=name,
            environment=environment,
            limits=limits or WorkspaceLimits(),
            settings=settings or WorkspaceSettings(),
            metadata=metadata or {},
        )
        self._workspaces[ws.workspace_id] = ws
        logger.info(f"[WORKSPACE MANAGER] Created workspace '{name}' (ID: {ws.workspace_id}, Org: {organization_id}, Env: {environment.value})")
        return ws

    def get_workspace(self, workspace_id: str) -> Workspace:
        """Get workspace by ID."""
        ws = self._workspaces.get(workspace_id)
        if not ws:
            raise WorkspaceNotFoundException(workspace_id)
        return ws

    def update_workspace(
        self,
        workspace_id: str,
        name: Optional[str] = None,
        environment: Optional[WorkspaceEnvironment] = None,
        limits: Optional[WorkspaceLimits] = None,
        settings: Optional[WorkspaceSettings] = None,
    ) -> Workspace:
        """Update workspace parameters."""
        ws = self.get_workspace(workspace_id)
        if name:
            ws.name = name
        if environment:
            ws.environment = environment
        if limits:
            ws.limits = limits
        if settings:
            ws.settings = settings
        ws.updated_at = datetime.now(timezone.utc)
        logger.info(f"[WORKSPACE MANAGER] Updated workspace '{workspace_id}'")
        return ws

    def archive_workspace(self, workspace_id: str) -> Workspace:
        """Archive a workspace."""
        ws = self.get_workspace(workspace_id)
        ws.is_archived = True
        ws.archived_at = datetime.now(timezone.utc)
        ws.updated_at = datetime.now(timezone.utc)
        logger.warning(f"[WORKSPACE MANAGER] Archived workspace '{workspace_id}'")
        return ws

    def delete_workspace(self, workspace_id: str) -> bool:
        """Delete a workspace."""
        ws = self.get_workspace(workspace_id)
        del self._workspaces[workspace_id]
        logger.error(f"[WORKSPACE MANAGER] Deleted workspace '{workspace_id}'")
        return True

    def list_workspaces(
        self,
        tenant_id: Optional[str] = None,
        organization_id: Optional[str] = None,
        environment: Optional[WorkspaceEnvironment] = None,
    ) -> List[Workspace]:
        """List workspaces filtered by tenant, organization, or environment."""
        res = list(self._workspaces.values())
        if tenant_id:
            res = [w for w in res if w.tenant_id == tenant_id]
        if organization_id:
            res = [w for w in res if w.organization_id == organization_id]
        if environment:
            res = [w for w in res if w.environment == environment]
        return res
