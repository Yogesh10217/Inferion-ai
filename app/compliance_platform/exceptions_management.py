"""Compliance Exception & Risk Acceptance Management Subsystem."""

from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone, timedelta
import uuid
from pydantic import BaseModel, Field

from app.compliance_platform.exceptions import CrossTenantComplianceAccessException


class ExceptionStatus(str, Enum):
    REQUESTED = "REQUESTED"
    RISK_EVALUATION = "RISK_EVALUATION"
    REQUIRES_APPROVAL = "REQUIRES_APPROVAL"
    APPROVED = "APPROVED"
    ACTIVE = "ACTIVE"
    EXPIRED = "EXPIRED"
    REVOKED = "REVOKED"
    REJECTED = "REJECTED"


class RiskAcceptance(BaseModel):
    accepted_by: str
    rationale: str
    risk_score: float = 50.0


class ComplianceExceptionRequest(BaseModel):
    exception_id: str = Field(default_factory=lambda: f"exc_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    requirement_id: str
    control_id: Optional[str] = None
    justification: str
    status: ExceptionStatus = ExceptionStatus.ACTIVE
    risk_acceptance: RiskAcceptance
    compensating_controls: List[str] = Field(default_factory=list)
    valid_from: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    valid_until: datetime = Field(default_factory=lambda: datetime.now(timezone.utc) + timedelta(days=30))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def is_active(self) -> bool:
        now = datetime.now(timezone.utc)
        return self.status == ExceptionStatus.ACTIVE and self.valid_from <= now <= self.valid_until


class ExceptionManager:
    """Manages compliance exceptions, risk acceptances, and automatic expiration handling."""

    def __init__(self) -> None:
        self._exceptions: Dict[str, ComplianceExceptionRequest] = {}

    def request_exception(
        self,
        tenant_id: str,
        requirement_id: str,
        justification: str,
        accepted_by: str = "risk_officer",
        compensating_controls: Optional[List[str]] = None,
        duration_days: int = 30,
    ) -> ComplianceExceptionRequest:
        now = datetime.now(timezone.utc)
        exc = ComplianceExceptionRequest(
            tenant_id=tenant_id,
            requirement_id=requirement_id,
            justification=justification,
            risk_acceptance=RiskAcceptance(accepted_by=accepted_by, rationale=justification),
            compensating_controls=compensating_controls or [],
            valid_from=now,
            valid_until=now + timedelta(days=duration_days),
            status=ExceptionStatus.ACTIVE,
        )
        self._exceptions[exc.exception_id] = exc
        return exc

    def get_exception(self, exception_id: str, tenant_id: str) -> ComplianceExceptionRequest:
        exc = self._exceptions.get(exception_id)
        if not exc:
            raise KeyError(f"Compliance exception '{exception_id}' not found.")
        if exc.tenant_id != tenant_id and tenant_id != "global":
            raise CrossTenantComplianceAccessException(request_tenant=tenant_id, target_tenant=exc.tenant_id, resource_id=exception_id)

        if not exc.is_active() and exc.status == ExceptionStatus.ACTIVE:
            exc.status = ExceptionStatus.EXPIRED

        return exc

    def expire_exception_explicitly(self, exception_id: str, tenant_id: str) -> ComplianceExceptionRequest:
        exc = self.get_exception(exception_id, tenant_id)
        exc.valid_until = datetime.now(timezone.utc) - timedelta(seconds=1)
        exc.status = ExceptionStatus.EXPIRED
        return exc

    def is_requirement_excepted(self, tenant_id: str, requirement_id: str) -> bool:
        for exc in self._exceptions.values():
            if exc.tenant_id == tenant_id and exc.requirement_id == requirement_id and exc.is_active():
                return True
        return False
