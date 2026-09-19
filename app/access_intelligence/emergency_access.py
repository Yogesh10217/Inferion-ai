"""Emergency & Break-Glass Access Governance (Phase 5.39)."""

import hashlib
import uuid
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.access_intelligence.exceptions import (
    AccessIntelligenceException,
    CrossTenantAccessIntelligenceException,
    InvalidAccessStateTransitionException,
)


class EmergencyAccessReason(str, Enum):
    SYSTEM_OUTAGE = "SYSTEM_OUTAGE"
    SECURITY_INCIDENT = "SECURITY_INCIDENT"
    DATA_CORRUPTION = "DATA_CORRUPTION"
    CRITICAL_DEPLOYMENT = "CRITICAL_DEPLOYMENT"


class EmergencyAccessStatus(str, Enum):
    REQUESTED = "REQUESTED"
    ACTIVE = "ACTIVE"
    REVIEWED = "REVIEWED"
    EXPIRED = "EXPIRED"
    CONCLUDED = "CONCLUDED"


class EmergencyAccessVerification(BaseModel):
    """Post-emergency audit verification entry."""

    verification_id: str = Field(default_factory=lambda: f"em_verif_{uuid.uuid4().hex[:8]}")
    verified_by: str
    passed: bool
    notes: str
    verified_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class EmergencyAccessRequest(BaseModel):
    """Break-glass Emergency Access Request."""

    request_id: str = Field(default_factory=lambda: f"em_req_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    requester_identity_id: str
    reason: EmergencyAccessReason
    justification: str
    time_bound_minutes: int = 120
    status: EmergencyAccessStatus = EmergencyAccessStatus.REQUESTED
    audit_fingerprint: str = ""
    requested_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    activated_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    verifications: List[EmergencyAccessVerification] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class EmergencyAccessManager:
    """Manages break-glass emergency access governance."""

    def __init__(self) -> None:
        self._requests: Dict[str, EmergencyAccessRequest] = {}

    def request_emergency_access(
        self,
        tenant_id: str,
        requester_identity_id: str,
        reason: EmergencyAccessReason,
        justification: str,
        time_bound_minutes: int = 120,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> EmergencyAccessRequest:
        if not justification or len(justification.strip()) < 10:
            raise AccessIntelligenceException(
                "Explicit, detailed justification (min 10 chars) required for emergency access."
            )

        req = EmergencyAccessRequest(
            tenant_id=tenant_id,
            requester_identity_id=requester_identity_id,
            reason=reason,
            justification=justification,
            time_bound_minutes=time_bound_minutes,
            metadata=metadata or {},
        )

        # Calculate SHA-256 fingerprint for audit evidence
        raw_data = f"{tenant_id}:{requester_identity_id}:{reason.value}:{justification}:{req.requested_at.isoformat()}"
        req.audit_fingerprint = hashlib.sha256(raw_data.encode("utf-8")).hexdigest()

        self._requests[req.request_id] = req
        return req

    def activate_emergency_access(self, tenant_id: str, request_id: str) -> EmergencyAccessRequest:
        req = self.get_request(tenant_id, request_id)
        if req.status != EmergencyAccessStatus.REQUESTED:
            raise InvalidAccessStateTransitionException(req.status.value, EmergencyAccessStatus.ACTIVE.value)
        req.status = EmergencyAccessStatus.ACTIVE
        req.activated_at = datetime.now(timezone.utc)
        req.expires_at = req.activated_at + timedelta(minutes=req.time_bound_minutes)
        return req

    def conclude_emergency_access(
        self, tenant_id: str, request_id: str, verifier_id: str, notes: str
    ) -> EmergencyAccessRequest:
        req = self.get_request(tenant_id, request_id)
        verif = EmergencyAccessVerification(
            verified_by=verifier_id,
            passed=True,
            notes=notes,
        )
        req.verifications.append(verif)
        req.status = EmergencyAccessStatus.CONCLUDED
        return req

    def get_request(self, tenant_id: str, request_id: str) -> EmergencyAccessRequest:
        req = self._requests.get(request_id)
        if not req or req.tenant_id != tenant_id:
            raise CrossTenantAccessIntelligenceException()
        return req
