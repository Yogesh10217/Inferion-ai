"""Emergency Access Governance."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List

from pydantic import BaseModel, Field

from app.identity_assurance.exceptions import (
    CrossTenantIdentityAssuranceException,
)


class EmergencyAccessStatus(str, Enum):
    REQUESTED = "REQUESTED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    ACTIVE = "ACTIVE"
    EXPIRED = "EXPIRED"
    TERMINATED = "TERMINATED"


class EmergencyAccessRisk(BaseModel):
    risk_score: float = 0.8  # Emergency access is inherently high risk
    requires_approval: bool = True
    risk_factors: List[str] = Field(default_factory=lambda: ["Break-glass emergency access requested"])


class EmergencyAccessRequest(BaseModel):
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    requestor_identity_id: str
    target_role: str = "BreakGlassAdmin"
    justification: str
    duration_minutes: int = 60
    status: EmergencyAccessStatus = EmergencyAccessStatus.REQUESTED
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class EmergencyAccessAssessment(BaseModel):
    assessment_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    request_id: str
    tenant_id: str
    risk: EmergencyAccessRisk = Field(default_factory=EmergencyAccessRisk)
    outcome: str = "REQUIRE_APPROVAL"
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class EmergencyAccessManager:
    """Manages emergency (break-glass) access governance."""

    def __init__(self) -> None:
        self._requests: Dict[str, EmergencyAccessRequest] = {}
        self._assessments: Dict[str, EmergencyAccessAssessment] = {}

    def request_emergency_access(
        self,
        tenant_id: str,
        requestor_identity_id: str,
        justification: str,
        target_role: str = "BreakGlassAdmin",
        duration_minutes: int = 60,
    ) -> EmergencyAccessRequest:
        req = EmergencyAccessRequest(
            tenant_id=tenant_id,
            requestor_identity_id=requestor_identity_id,
            target_role=target_role,
            justification=justification,
            duration_minutes=duration_minutes,
        )
        self._requests[req.request_id] = req

        # Emergency access ALWAYS requires approval
        assessment = EmergencyAccessAssessment(
            request_id=req.request_id,
            tenant_id=tenant_id,
            risk=EmergencyAccessRisk(),
            outcome="REQUIRE_APPROVAL",
        )
        self._assessments[req.request_id] = assessment
        return req

    def get_request(self, tenant_id: str, request_id: str) -> EmergencyAccessRequest:
        req = self._requests.get(request_id)
        if not req or req.tenant_id != tenant_id:
            raise CrossTenantIdentityAssuranceException()
        return req

    def get_assessment(self, tenant_id: str, request_id: str) -> EmergencyAccessAssessment:
        assessment = self._assessments.get(request_id)
        if not assessment or assessment.tenant_id != tenant_id:
            raise CrossTenantIdentityAssuranceException()
        return assessment
