"""Service & Workload Short-Lived Credential Management Subsystem."""

import logging
import uuid
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from app.security.secrets import SecretManager

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class WorkloadType(str, Enum):
    WORKER = "WORKER"
    AGENT = "AGENT"
    AGENT_TEAM = "AGENT_TEAM"
    WORKFLOW = "WORKFLOW"
    MCP_SERVER = "MCP_SERVER"
    EXTENSION = "EXTENSION"
    CONNECTOR = "CONNECTOR"
    BACKGROUND_JOB = "BACKGROUND_JOB"
    SDK_CLIENT = "SDK_CLIENT"
    INTERNAL_SERVICE = "INTERNAL_SERVICE"


class WorkloadCredential(BaseModel):
    credential_id: str = Field(default_factory=lambda: f"wcred_{uuid.uuid4().hex[:10]}")
    workload_id: str
    tenant_id: str = "global"
    token_value: str = Field(default_factory=lambda: f"wtok_{uuid.uuid4().hex}")
    issued_at: datetime = Field(default_factory=_now)
    expires_at: datetime = Field(default_factory=lambda: _now() + timedelta(hours=1))


class WorkloadIdentity(BaseModel):
    workload_id: str = Field(default_factory=lambda: f"wkld_{uuid.uuid4().hex[:10]}")
    name: str
    workload_type: WorkloadType = WorkloadType.WORKER
    tenant_id: str = "global"

    allowed_scopes: List[str] = Field(default_factory=list)
    is_active: bool = True
    created_at: datetime = Field(default_factory=_now)


class WorkloadIdentityManager:
    """Issues short-lived credentials and manages workload identities across platform components."""

    def __init__(self, secret_manager: Optional[SecretManager] = None) -> None:
        self.secret_manager = secret_manager or SecretManager()
        self._workloads: Dict[str, WorkloadIdentity] = {}
        self._credentials: Dict[str, WorkloadCredential] = {}

    def register_workload(
        self,
        name: str,
        workload_type: WorkloadType = WorkloadType.WORKER,
        tenant_id: str = "global",
        allowed_scopes: Optional[List[str]] = None,
    ) -> WorkloadIdentity:
        wkld = WorkloadIdentity(
            name=name,
            workload_type=workload_type,
            tenant_id=tenant_id,
            allowed_scopes=allowed_scopes or ["read"],
        )
        self._workloads[wkld.workload_id] = wkld
        logger.info(
            f"[WORKLOAD IDENTITY] Registered workload '{wkld.workload_id}' ({name}, {workload_type.value}) for tenant '{tenant_id}'"
        )
        return wkld

    def issue_credential(self, workload_id: str, ttl_minutes: int = 60) -> WorkloadCredential:
        wkld = self.get_workload(workload_id)
        now = _now()
        cred = WorkloadCredential(
            workload_id=workload_id,
            tenant_id=wkld.tenant_id,
            issued_at=now,
            expires_at=now + timedelta(minutes=ttl_minutes),
        )
        self._credentials[cred.credential_id] = cred
        logger.info(
            f"[WORKLOAD IDENTITY] Issued short-lived credential '{cred.credential_id}' for workload '{workload_id}' (TTL: {ttl_minutes}m)"
        )
        return cred

    def get_workload(self, workload_id: str) -> WorkloadIdentity:
        wkld = self._workloads.get(workload_id)
        if not wkld:
            raise KeyError(f"Workload identity '{workload_id}' not found")
        return wkld
