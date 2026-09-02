"""Privileged Access Governance (Phase 5.39)."""

from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone, timedelta
import uuid
from pydantic import BaseModel, Field

from app.access_intelligence.exceptions import (
    PrivilegedAccessNotFoundException,
    CrossTenantAccessIntelligenceException,
    HighRiskAccessRequiresApprovalException,
    InvalidAccessStateTransitionException,
)


class PrivilegedAccessScope(str, Enum):
    PRODUCTION = "PRODUCTION"
    ADMIN = "ADMIN"
    EMERGENCY = "EMERGENCY"
    SERVICE_ELEVATION = "SERVICE_ELEVATION"


class PrivilegedAccessStatus(str, Enum):
    PENDING_APPROVAL = "PENDING_APPROVAL"
    APPROVED = "APPROVED"
    ACTIVATED = "ACTIVATED"
    EXPIRED = "EXPIRED"
    REVOKED = "REVOKED"
    REJECTED = "REJECTED"


class PrivilegedAccessDuration(BaseModel):
    """Duration specification for JIT / temporary privileged access."""
    duration_minutes: int = 60
    max_allowed_minutes: int = 480


class PrivilegedAccessRequest(BaseModel):
    """Privileged Access Request representation."""
    request_id: str = Field(default_factory=lambda: f"priv_req_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    requester_identity_id: str
    target_role_or_entitlement: str
    scope: PrivilegedAccessScope
    justification: str
    duration: PrivilegedAccessDuration = Field(default_factory=PrivilegedAccessDuration)
    status: PrivilegedAccessStatus = PrivilegedAccessStatus.PENDING_APPROVAL
    requires_approval: bool = True
    approval_id: Optional[str] = None
    requested_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    activated_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class PrivilegedAccessManager:
    """Privileged Access Governance Manager."""

    def __init__(self) -> None:
        self._requests: Dict[str, PrivilegedAccessRequest] = {}

    def request_privileged_access(
        self,
        tenant_id: str,
        requester_identity_id: str,
        target_role_or_entitlement: str,
        scope: PrivilegedAccessScope,
        justification: str,
        duration_minutes: int = 60,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> PrivilegedAccessRequest:
        requires_appr = scope in [PrivilegedAccessScope.PRODUCTION, PrivilegedAccessScope.ADMIN, PrivilegedAccessScope.EMERGENCY]
        
        req = PrivilegedAccessRequest(
            tenant_id=tenant_id,
            requester_identity_id=requester_identity_id,
            target_role_or_entitlement=target_role_or_entitlement,
            scope=scope,
            justification=justification,
            duration=PrivilegedAccessDuration(duration_minutes=duration_minutes),
            status=PrivilegedAccessStatus.PENDING_APPROVAL if requires_appr else PrivilegedAccessStatus.APPROVED,
            requires_approval=requires_appr,
            metadata=metadata or {},
        )
        self._requests[req.request_id] = req
        return req

    def approve_request(self, tenant_id: str, request_id: str, approver_id: str, approval_id: str = "appr_123") -> PrivilegedAccessRequest:
        req = self.get_request(tenant_id, request_id)
        if req.status != PrivilegedAccessStatus.PENDING_APPROVAL:
            raise InvalidAccessStateTransitionException(req.status.value, PrivilegedAccessStatus.APPROVED.value)
        req.status = PrivilegedAccessStatus.APPROVED
        req.approval_id = approval_id
        return req

    def activate_request(self, tenant_id: str, request_id: str) -> PrivilegedAccessRequest:
        req = self.get_request(tenant_id, request_id)
        if req.requires_approval and req.status != PrivilegedAccessStatus.APPROVED:
            raise HighRiskAccessRequiresApprovalException(req.request_id, 90.0)
        req.status = PrivilegedAccessStatus.ACTIVATED
        req.activated_at = datetime.now(timezone.utc)
        req.expires_at = req.activated_at + timedelta(minutes=req.duration.duration_minutes)
        return req

    def get_request(self, tenant_id: str, request_id: str) -> PrivilegedAccessRequest:
        req = self._requests.get(request_id)
        if not req or req.tenant_id != tenant_id:
            raise CrossTenantAccessIntelligenceException()
        return req

    def list_requests(self, tenant_id: str, scope: Optional[PrivilegedAccessScope] = None) -> List[PrivilegedAccessRequest]:
        results = [r for r in self._requests.values() if r.tenant_id == tenant_id]
        if scope:
            results = [r for r in results if r.scope == scope]
        return results
