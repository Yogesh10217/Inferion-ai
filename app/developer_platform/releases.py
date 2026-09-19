"""Software Release Intelligence & Management Subsystem."""

import logging
import uuid
from datetime import datetime, timezone
from typing import Dict, Optional

from pydantic import BaseModel, Field

from app.operations.manager import OperationsManager

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class SoftwareRelease(BaseModel):
    release_id: str = Field(default_factory=lambda: f"rel_{uuid.uuid4().hex[:10]}")
    project_id: str
    version: str = "1.0.0"
    tenant_id: str = "global"
    status: str = "DEPLOYED"
    created_at: datetime = Field(default_factory=_now)


class ReleaseManager:
    """Manages software releases and integrates deployment verification with OperationsManager."""

    def __init__(self, operations_manager: Optional[OperationsManager] = None) -> None:
        self.operations_manager = operations_manager or OperationsManager()
        self._releases: Dict[str, SoftwareRelease] = {}

    def create_release(self, project_id: str, version: str, tenant_id: str = "global") -> SoftwareRelease:
        rel = SoftwareRelease(project_id=project_id, version=version, tenant_id=tenant_id)
        self._releases[rel.release_id] = rel
        logger.info(
            f"[RELEASE MANAGER] Created software release '{rel.release_id}' (v{version}) for project '{project_id}'"
        )
        return rel
