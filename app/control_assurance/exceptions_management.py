"""Controlled Policy/Control Exception Workflow Subsystem (Phase 5.38)."""

from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone, timedelta
import uuid
from pydantic import BaseModel, Field

from app.platform_contracts.tenant import TenantAccessGuard
from app.control_assurance.exceptions import (
    HighRiskControlOverrideRequiresApprovalException,
    CrossTenantControlAssuranceAccessException,
)


class ControlExceptionStatus(str, Enum):
    REQUESTED = "REQUESTED"
    UNDER_REVIEW = "UNDER_REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"


class ControlExceptionJustification(BaseModel):
    business_reason: str
    compensating_controls: List[str] = Field(default_factory=list)
    risk_acceptance: str = "ACCEPTED_BY_CISO"


class ControlExceptionApproval(BaseModel):
    approver_id: str
    approved_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    comments: Optional[str] = None


class ControlExceptionRequest(BaseModel):
    exception_id: str = Field(default_factory=lambda: f"cex_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    control_id: str
    status: ControlExceptionStatus = ControlExceptionStatus.REQUESTED
    justification: ControlExceptionJustification
    approval: Optional[ControlExceptionApproval] = None
    is_critical_control: bool = False
    expires_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc) + timedelta(days=30))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ControlExceptionManager:
    """Manages control exception requests, approvals, and expiration lifecycle."""

    def __init__(self, tenant_guard: Optional[TenantAccessGuard] = None) -> None:
        self.tenant_guard = tenant_guard or TenantAccessGuard()
        self._exceptions: Dict[str, ControlExceptionRequest] = {}

    def request_exception(
        self,
        tenant_id: str,
        control_id: str,
        business_reason: str,
        is_critical_control: bool = False,
        expires_in_days: int = 30,
    ) -> ControlExceptionRequest:
        req = ControlExceptionRequest(
            tenant_id=tenant_id,
            control_id=control_id,
            justification=ControlExceptionJustification(business_reason=business_reason),
            is_critical_control=is_critical_control,
            expires_at=datetime.now(timezone.utc) + timedelta(days=expires_in_days),
        )
        self._exceptions[req.exception_id] = req

        if is_critical_control:
            raise HighRiskControlOverrideRequiresApprovalException(control_id, "CRITICAL")

        return req

    def approve_exception(self, exception_id: str, tenant_id: str, approver_id: str) -> ControlExceptionRequest:
        req = self.get_exception(exception_id, tenant_id)
        req.status = ControlExceptionStatus.APPROVED
        req.approval = ControlExceptionApproval(approver_id=approver_id)
        return req

    def get_exception(self, exception_id: str, tenant_id: str) -> ControlExceptionRequest:
        req = self._exceptions.get(exception_id)
        if not req:
            raise CrossTenantControlAssuranceAccessException()
        try:
            self.tenant_guard.enforce_isolation(tenant_id, req.tenant_id)
        except Exception:
            raise CrossTenantControlAssuranceAccessException()

        # Check expiration
        if datetime.now(timezone.utc) > req.expires_at:
            req.status = ControlExceptionStatus.EXPIRED

        return req
