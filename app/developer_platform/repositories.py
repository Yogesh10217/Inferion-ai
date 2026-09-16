"""Repository Management & Git Integration Subsystem."""

import logging
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from app.integrations.manager import IntegrationManager

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class RepositoryBranch(BaseModel):
    name: str = "main"
    commit_sha: str = "head"
    is_protected: bool = False


class ProjectRepository(BaseModel):
    repository_id: str = Field(default_factory=lambda: f"repo_{uuid.uuid4().hex[:10]}")
    project_id: str
    name: str
    provider: str = "github"
    default_branch: str = "main"
    branches: List[RepositoryBranch] = Field(default_factory=lambda: [RepositoryBranch()])
    tenant_id: str = "global"
    created_at: datetime = Field(default_factory=_now)


class RepositoryManager:
    """Manages Git repositories and delegates external API calls to IntegrationManager."""

    def __init__(self, integration_manager: Optional[IntegrationManager] = None) -> None:
        self.integration_manager = integration_manager or IntegrationManager()
        self._repositories: Dict[str, ProjectRepository] = {}

    def register_repository(self, project_id: str, name: str, provider: str = "github", tenant_id: str = "global") -> ProjectRepository:
        repo = ProjectRepository(project_id=project_id, name=name, provider=provider, tenant_id=tenant_id)
        self._repositories[repo.repository_id] = repo
        logger.info(f"[REPOSITORY MANAGER] Registered repository '{repo.repository_id}' ('{name}') for project '{project_id}'")
        return repo

    def get_repository(self, repository_id: str) -> ProjectRepository:
        return self._repositories[repository_id]
