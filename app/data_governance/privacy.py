"""Privacy Governance & Subject Rights Request Subsystem."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

from app.data_governance.exceptions import DataGovernanceException


class PrivacyRequestType(str, Enum):
    ACCESS = "ACCESS"
    RESTRICT = "RESTRICT"
    ERASURE_REQUEST = "ERASURE_REQUEST"
    EXPORT_REQUEST = "EXPORT_REQUEST"
    CONSENT_WITHDRAWAL = "CONSENT_WITHDRAWAL"
    PROCESSING_RESTRICTION = "PROCESSING_RESTRICTION"


class PrivacyRequestStatus(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    COMPLETED = "COMPLETED"


class PrivacyPolicy(BaseModel):
    policy_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    name: str
    version: str = "1.0.0"
    allow_export: bool = True
    allow_erasure: bool = True
    retention_period_days: int = 365
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class PrivacyRequest(BaseModel):
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    subject_id: str
    request_type: PrivacyRequestType
    status: PrivacyRequestStatus = PrivacyRequestStatus.PENDING
    details: Dict[str, Any] = Field(default_factory=dict)
    idempotency_key: str = Field(default_factory=lambda: str(uuid.uuid4()))
    submitted_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None


class PrivacyDecision(BaseModel):
    decision_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    request_id: str
    approved: bool
    reason: str
    policy_version: str = "1.0.0"
    decided_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class PrivacyManager:
    """Manages privacy policies and Data Subject Rights requests."""

    def __init__(self) -> None:
        self._policies: Dict[str, PrivacyPolicy] = {}
        self._requests: Dict[str, PrivacyRequest] = {}
        self._processed_idempotency_keys: Dict[str, PrivacyRequest] = {}

    def get_or_create_policy(self, tenant_id: str) -> PrivacyPolicy:
        if tenant_id not in self._policies:
            self._policies[tenant_id] = PrivacyPolicy(tenant_id=tenant_id, name=f"Default Policy {tenant_id}")
        return self._policies[tenant_id]

    def submit_privacy_request(
        self,
        tenant_id: str,
        subject_id: str,
        request_type: PrivacyRequestType,
        details: Optional[Dict[str, Any]] = None,
        idempotency_key: Optional[str] = None,
    ) -> PrivacyRequest:
        ikey = idempotency_key or f"{tenant_id}:{subject_id}:{request_type.value}:{datetime.now(timezone.utc).date()}"
        if ikey in self._processed_idempotency_keys:
            return self._processed_idempotency_keys[ikey]

        req = PrivacyRequest(
            tenant_id=tenant_id,
            subject_id=subject_id,
            request_type=request_type,
            details=details or {},
            idempotency_key=ikey,
        )
        self._requests[req.request_id] = req
        self._processed_idempotency_keys[ikey] = req
        return req

    def process_privacy_request(self, request_id: str, tenant_id: str, approve: bool, reason: str) -> PrivacyDecision:
        req = self._requests.get(request_id)
        if not req or req.tenant_id != tenant_id:
            raise DataGovernanceException(f"Privacy request '{request_id}' not found.", tenant_id=tenant_id)

        if approve:
            req.status = PrivacyRequestStatus.COMPLETED
            req.completed_at = datetime.now(timezone.utc)
        else:
            req.status = PrivacyRequestStatus.REJECTED

        policy = self.get_or_create_policy(tenant_id)
        decision = PrivacyDecision(
            request_id=request_id,
            approved=approve,
            reason=reason,
            policy_version=policy.version,
        )
        return decision
