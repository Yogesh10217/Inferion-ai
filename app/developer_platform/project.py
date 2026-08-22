"""Developer Project domain entity & lifecycle management."""

import logging
from enum import Enum
from typing import Dict, Any, Optional, List, Set
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.developer_platform.exceptions import ProjectNotFoundException, InvalidProjectLifecycleTransition

logger = logging.getLogger(__name__)


class ProjectLifecycle(str, Enum):
    CREATED = "CREATED"
    DEVELOPMENT = "DEVELOPMENT"
    TESTING = "TESTING"
    STAGED = "STAGED"
    PUBLISHED = "PUBLISHED"
    DEPRECATED = "DEPRECATED"
    ARCHIVED = "ARCHIVED"


VALID_PROJECT_TRANSITIONS = {
    ProjectLifecycle.CREATED: {ProjectLifecycle.DEVELOPMENT, ProjectLifecycle.ARCHIVED},
    ProjectLifecycle.DEVELOPMENT: {ProjectLifecycle.TESTING, ProjectLifecycle.ARCHIVED},
    ProjectLifecycle.TESTING: {ProjectLifecycle.DEVELOPMENT, ProjectLifecycle.STAGED, ProjectLifecycle.ARCHIVED},
    ProjectLifecycle.STAGED: {ProjectLifecycle.TESTING, ProjectLifecycle.PUBLISHED, ProjectLifecycle.ARCHIVED},
    ProjectLifecycle.PUBLISHED: {ProjectLifecycle.DEPRECATED, ProjectLifecycle.ARCHIVED},
    ProjectLifecycle.DEPRECATED: {ProjectLifecycle.ARCHIVED},
    ProjectLifecycle.ARCHIVED: set(),
}


class DeveloperProject(BaseModel):
    """Developer project entity container."""

    project_id: str = Field(default_factory=lambda: f"proj_{uuid.uuid4().hex[:10]}")
    tenant_id: str = "global"
    organization_id: str
    workspace_id: str
    developer_id: str
    name: str
    description: str = ""
    version: str = "0.1.0"
    lifecycle: ProjectLifecycle = ProjectLifecycle.CREATED
    repository_url: Optional[str] = None
    runtime_config: Dict[str, Any] = Field(default_factory=dict)
    associated_extension_ids: Set[str] = Field(default_factory=set)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ProjectManager:
    """Manages developer projects, lifecycle state transitions, environment scoping, and extension associations."""

    def __init__(self) -> None:
        self._projects: Dict[str, DeveloperProject] = {}

    def create_project(
        self,
        name: str,
        organization_id: str,
        workspace_id: str,
        developer_id: str,
        tenant_id: str = "global",
        description: str = "",
        repository_url: Optional[str] = None,
        runtime_config: Optional[Dict[str, Any]] = None,
    ) -> DeveloperProject:
        """Create a new developer project."""
        proj = DeveloperProject(
            name=name,
            organization_id=organization_id,
            workspace_id=workspace_id,
            developer_id=developer_id,
            tenant_id=tenant_id,
            description=description,
            repository_url=repository_url,
            runtime_config=runtime_config or {},
        )
        self._projects[proj.project_id] = proj
        logger.info(f"[PROJECT MANAGER] Created project '{name}' (ID: {proj.project_id}, Dev: {developer_id})")
        return proj

    def get_project(self, project_id: str) -> DeveloperProject:
        proj = self._projects.get(project_id)
        if not proj:
            raise ProjectNotFoundException(project_id)
        return proj

    def transition_lifecycle(self, project_id: str, target_state: ProjectLifecycle) -> DeveloperProject:
        """Transition project to target lifecycle state with validation."""
        proj = self.get_project(project_id)
        current = proj.lifecycle

        if current != target_state and target_state not in VALID_PROJECT_TRANSITIONS.get(current, set()):
            raise InvalidProjectLifecycleTransition(current.value, target_state.value)

        proj.lifecycle = target_state
        proj.updated_at = datetime.now(timezone.utc)
        logger.info(f"[PROJECT MANAGER] Project '{project_id}' transitioned {current.value} -> {target_state.value}")
        return proj

    def associate_extension(self, project_id: str, extension_id: str) -> DeveloperProject:
        """Associate extension ID with project."""
        proj = self.get_project(project_id)
        proj.associated_extension_ids.add(extension_id)
        proj.updated_at = datetime.now(timezone.utc)
        return proj

    def list_projects(
        self,
        tenant_id: Optional[str] = None,
        organization_id: Optional[str] = None,
        developer_id: Optional[str] = None,
    ) -> List[DeveloperProject]:
        res = list(self._projects.values())
        if tenant_id:
            res = [p for p in res if p.tenant_id == tenant_id]
        if organization_id:
            res = [p for p in res if p.organization_id == organization_id]
        if developer_id:
            res = [p for p in res if p.developer_id == developer_id]
        return res
