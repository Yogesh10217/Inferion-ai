"""Developer Project & Membership Management Subsystem."""

from datetime import datetime, timezone
from enum import Enum
import uuid
import logging
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field

from app.developer_platform.exceptions import ProjectNotFoundException

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class ProjectStatus(str, Enum):
    CREATED = "CREATED"
    CONFIGURED = "CONFIGURED"
    ACTIVE = "ACTIVE"
    ARCHIVED = "ARCHIVED"
    DELETED = "DELETED"


ProjectLifecycle = ProjectStatus



class ProjectMember(BaseModel):
    member_id: str = Field(default_factory=lambda: f"pmem_{uuid.uuid4().hex[:10]}")
    user_id: str
    role: str = "DEVELOPER"
    added_at: datetime = Field(default_factory=_now)


class DeveloperProject(BaseModel):
    project_id: str = Field(default_factory=lambda: f"dproj_{uuid.uuid4().hex[:10]}")
    name: str
    description: str = ""
    status: ProjectStatus = ProjectStatus.ACTIVE
    tenant_id: str = "global"
    members: List[ProjectMember] = Field(default_factory=list)
    repository_ids: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=_now)
    updated_at: datetime = Field(default_factory=_now)


class ProjectManager:
    """Manages developer projects and membership roles."""

    def __init__(self) -> None:
        self._projects: Dict[str, DeveloperProject] = {}

    def create_project(
        self,
        name: str,
        description: str = "",
        tenant_id: str = "global",
        organization_id: str = "org_default",
        workspace_id: str = "ws_default",
        developer_id: str = "dev_default",
        repository_url: Optional[str] = None,
    ) -> DeveloperProject:
        proj = DeveloperProject(name=name, description=description, tenant_id=tenant_id)
        self._projects[proj.project_id] = proj
        logger.info(f"[PROJECT MANAGER] Created project '{proj.project_id}' ('{name}') for tenant '{tenant_id}'")
        return proj


    def get_project(self, project_id: str) -> DeveloperProject:
        proj = self._projects.get(project_id)
        if not proj or proj.status == ProjectStatus.DELETED:
            raise ProjectNotFoundException(project_id)
        return proj

    def list_projects(self, tenant_id: Optional[str] = None, developer_id: Optional[str] = None) -> List[DeveloperProject]:
        res = [p for p in self._projects.values() if p.status != ProjectStatus.DELETED]
        if tenant_id:
            res = [r for r in res if r.tenant_id == tenant_id]
        return res

