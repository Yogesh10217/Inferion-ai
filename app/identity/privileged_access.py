"""Just-In-Time (JIT) Privileged Access Management Subsystem."""

import logging
import uuid
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Dict, Optional

from pydantic import BaseModel, Field

from app.approvals.approval_engine import ApprovalEngine

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class PrivilegedRole(str, Enum):
    PLATFORM_ADMIN = "PLATFORM_ADMIN"
    SECURITY_ADMIN = "SECURITY_ADMIN"
    TENANT_ADMIN = "TENANT_ADMIN"
    DATABASE_ADMIN = "DATABASE_ADMIN"
    ML_ADMIN = "ML_ADMIN"
    FINOPS_ADMIN = "FINOPS_ADMIN"
    OPERATIONS_ADMIN = "OPERATIONS_ADMIN"
    GOVERNANCE_ADMIN = "GOVERNANCE_ADMIN"
    DEVELOPER_ADMIN = "DEVELOPER_ADMIN"


class PrivilegedAccessStatus(str, Enum):
    REQUESTED = "REQUESTED"
    APPROVED = "APPROVED"
    ACTIVE = "ACTIVE"
    EXPIRED = "EXPIRED"
    REVOKED = "REVOKED"
    DENIED = "DENIED"


class PrivilegedAccessGrant(BaseModel):
    grant_id: str = Field(default_factory=lambda: f"jit_{uuid.uuid4().hex[:10]}")
    identity_id: str
    tenant_id: str = "global"
    role: PrivilegedRole = PrivilegedRole.TENANT_ADMIN
    status: PrivilegedAccessStatus = PrivilegedAccessStatus.REQUESTED

    approval_request_id: Optional[str] = None
    duration_minutes: int = 60
    granted_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    revoked_at: Optional[datetime] = None


class PrivilegedAccessManager:
    """Manages JIT temporary privileged access elevation and ApprovalEngine authorization workflows."""

    def __init__(self, approval_engine: Optional[ApprovalEngine] = None) -> None:
        self.approval_engine = approval_engine or ApprovalEngine()
        self._grants: Dict[str, PrivilegedAccessGrant] = {}

    def request_privileged_access(
        self,
        identity_id: str,
        role: PrivilegedRole,
        tenant_id: str = "global",
        duration_minutes: int = 60,
    ) -> PrivilegedAccessGrant:
        req_id = f"appr_jit_{uuid.uuid4().hex[:8]}"
        grant = PrivilegedAccessGrant(
            identity_id=identity_id,
            tenant_id=tenant_id,
            role=role,
            status=PrivilegedAccessStatus.REQUESTED,
            approval_request_id=req_id,
            duration_minutes=duration_minutes,
        )
        self._grants[grant.grant_id] = grant
        logger.warning(f"[PRIVILEGED ACCESS] JIT request for role '{role.value}' by '{identity_id}' requires approval (ID: {req_id})")
        return grant

    def approve_grant(self, grant_id: str) -> PrivilegedAccessGrant:
        grant = self.get_grant(grant_id)
        now = _now()
        grant.status = PrivilegedAccessStatus.ACTIVE
        grant.granted_at = now
        grant.expires_at = now + timedelta(minutes=grant.duration_minutes)
        logger.info(f"[PRIVILEGED ACCESS] Grant '{grant_id}' APPROVED and ACTIVE until {grant.expires_at}")
        return grant

    def check_grant_validity(self, grant_id: str) -> bool:
        grant = self.get_grant(grant_id)
        if grant.status != PrivilegedAccessStatus.ACTIVE:
            return False
        if grant.expires_at and _now() > grant.expires_at:
            grant.status = PrivilegedAccessStatus.EXPIRED
            logger.info(f"[PRIVILEGED ACCESS] Grant '{grant_id}' EXPIRED automatically")
            return False
        return True

    def revoke_grant(self, grant_id: str, reason: str = "Administrator revocation") -> PrivilegedAccessGrant:
        grant = self.get_grant(grant_id)
        grant.status = PrivilegedAccessStatus.REVOKED
        grant.revoked_at = _now()
        logger.warning(f"[PRIVILEGED ACCESS] Grant '{grant_id}' REVOKED: {reason}")
        return grant

    def get_grant(self, grant_id: str) -> PrivilegedAccessGrant:
        grant = self._grants.get(grant_id)
        if not grant:
            raise KeyError(f"Privileged access grant '{grant_id}' not found")
        return grant
