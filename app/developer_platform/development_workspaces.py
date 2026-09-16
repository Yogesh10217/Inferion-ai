"""Developer Workspace & Ephemeral Session Subsystem."""

import logging
import uuid
from datetime import datetime, timezone
from typing import Dict, Optional

from pydantic import BaseModel, Field

from app.security.secrets import SecretManager

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class DeveloperWorkspace(BaseModel):
    workspace_id: str = Field(default_factory=lambda: f"dws_{uuid.uuid4().hex[:10]}")
    project_id: str
    developer_id: str
    tenant_id: str = "global"
    status: str = "READY"
    created_at: datetime = Field(default_factory=_now)


class WorkspaceSession(BaseModel):
    session_id: str = Field(default_factory=lambda: f"wsess_{uuid.uuid4().hex[:10]}")
    workspace_id: str
    secret_ref_id: str
    tenant_id: str = "global"
    is_active: bool = True
    created_at: datetime = Field(default_factory=_now)


class WorkspaceManager:
    """Manages ephemeral developer workspaces and short-lived credential sessions."""

    def __init__(self, secret_manager: Optional[SecretManager] = None) -> None:
        self.secret_manager = secret_manager or SecretManager()
        self._workspaces: Dict[str, DeveloperWorkspace] = {}
        self._sessions: Dict[str, WorkspaceSession] = {}

    def create_workspace(self, project_id: str, developer_id: str, tenant_id: str = "global") -> DeveloperWorkspace:
        ws = DeveloperWorkspace(project_id=project_id, developer_id=developer_id, tenant_id=tenant_id)
        self._workspaces[ws.workspace_id] = ws

        # Issue short-lived credential reference
        sec_key = f"ws_token_{ws.workspace_id}"
        self.secret_manager.set_secret(sec_key, f"temp-ws-token-{uuid.uuid4().hex}")
        sess = WorkspaceSession(workspace_id=ws.workspace_id, secret_ref_id=sec_key, tenant_id=tenant_id)
        self._sessions[sess.session_id] = sess

        logger.info(f"[WORKSPACE MANAGER] Created workspace '{ws.workspace_id}' with ephemeral session '{sess.session_id}'")
        return ws
