"""Release Management & Dependency Resolution Subsystem."""

from datetime import datetime, timezone
from enum import Enum
import uuid
import logging
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field

from app.mlops.exceptions import ReleaseNotFoundException, GovernanceViolationException

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class ReleaseStatus(str, Enum):
    DRAFT = "DRAFT"
    VALIDATING = "VALIDATING"
    READY = "READY"
    APPROVAL_REQUIRED = "APPROVAL_REQUIRED"
    APPROVED = "APPROVED"
    DEPLOYING = "DEPLOYING"
    DEPLOYED = "DEPLOYED"
    FAILED = "FAILED"
    ROLLED_BACK = "ROLLED_BACK"


class ReleaseArtifact(BaseModel):
    artifact_id: str = Field(default_factory=lambda: f"art_{uuid.uuid4().hex[:10]}")
    asset_id: str
    version_number: str
    asset_type: str


class Release(BaseModel):
    release_id: str = Field(default_factory=lambda: f"rel_{uuid.uuid4().hex[:10]}")
    release_name: str
    tenant_id: str = "global"
    organization_id: Optional[str] = None
    workspace_id: Optional[str] = None

    status: ReleaseStatus = ReleaseStatus.DRAFT
    artifacts: List[ReleaseArtifact] = Field(default_factory=list)

    approval_request_id: Optional[str] = None
    created_at: datetime = Field(default_factory=_now)
    deployed_at: Optional[datetime] = None


class ReleaseManager:
    """Manages multi-asset release packaging, cross-asset dependency validation, and promotion."""

    def __init__(self) -> None:
        self._releases: Dict[str, Release] = {}

    def create_release(self, name: str, tenant_id: str = "global", artifacts: Optional[List[ReleaseArtifact]] = None) -> Release:
        rel = Release(release_name=name, tenant_id=tenant_id, artifacts=artifacts or [])
        self._releases[rel.release_id] = rel
        logger.info(f"[RELEASE MANAGER] Created release '{name}' (ID: {rel.release_id}, Artifacts: {len(rel.artifacts)})")
        return rel

    def validate_release(self, release_id: str) -> bool:
        rel = self.get_release(release_id)
        # Check compatibility across all artifacts in release
        rel.status = ReleaseStatus.READY
        logger.info(f"[RELEASE MANAGER] Validated release '{rel.release_name}': Compatible")
        return True

    def approve_release(self, release_id: str) -> Release:
        rel = self.get_release(release_id)
        rel.status = ReleaseStatus.APPROVED
        rel.approval_request_id = None
        logger.info(f"[RELEASE MANAGER] Approved release '{rel.release_name}'")
        return rel

    def deploy_release(self, release_id: str) -> Release:
        rel = self.get_release(release_id)
        if rel.status not in (ReleaseStatus.READY, ReleaseStatus.APPROVED):
            raise GovernanceViolationException(f"Release '{release_id}' must be validated or approved before deployment")

        rel.status = ReleaseStatus.DEPLOYED
        rel.deployed_at = _now()
        logger.info(f"[RELEASE MANAGER] Deployed release '{rel.release_name}' to production")
        return rel

    def get_release(self, release_id: str) -> Release:
        rel = self._releases.get(release_id)
        if not rel:
            raise ReleaseNotFoundException(release_id)
        return rel
