"""Human Approval Ledger and Verification for Cross-Phase Actions (Phase 5.58)."""

import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional

logger = logging.getLogger(__name__)


@dataclass
class PlatformIntegrationApproval:
    approval_id: str
    tenant_id: str
    action: str
    decision: str  # PENDING, APPROVED, REJECTED, EXPIRED
    approver: Optional[str] = None
    reason: str = ""
    token: str = ""
    ttl_minutes: int = 60
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    resolved_at: Optional[datetime] = None

    @property
    def is_valid(self) -> bool:
        if self.decision != "APPROVED":
            return False
        now = datetime.now(timezone.utc)
        return (now - self.created_at) <= timedelta(minutes=self.ttl_minutes)


class PlatformIntegrationApprovalManager:
    """Manages human approval requests and validates approval tokens before delegation."""

    def __init__(self) -> None:
        # keyed by approval_id
        self._approvals: Dict[str, PlatformIntegrationApproval] = {}

    def request_approval(self, tenant_id: str, action: str, reason: str = "") -> PlatformIntegrationApproval:
        app_id = f"appr-{uuid.uuid4().hex[:12]}"
        token = f"tok-{uuid.uuid4().hex[:16]}"
        appr = PlatformIntegrationApproval(
            approval_id=app_id,
            tenant_id=tenant_id,
            action=action,
            decision="PENDING",
            reason=reason,
            token=token,
        )
        self._approvals[app_id] = appr
        logger.info(f"Requested approval {app_id} for action '{action}' (tenant: '{tenant_id}')")
        return appr

    def approve(self, approval_id: str, approver: str, reason: str = "Approved by admin") -> PlatformIntegrationApproval:
        appr = self._approvals.get(approval_id)
        if not appr:
            raise KeyError(f"Approval request '{approval_id}' not found.")
        appr.decision = "APPROVED"
        appr.approver = approver
        appr.reason = reason
        appr.resolved_at = datetime.now(timezone.utc)
        return appr

    def reject(self, approval_id: str, approver: str, reason: str = "Rejected by admin") -> PlatformIntegrationApproval:
        appr = self._approvals.get(approval_id)
        if not appr:
            raise KeyError(f"Approval request '{approval_id}' not found.")
        appr.decision = "REJECTED"
        appr.approver = approver
        appr.reason = reason
        appr.resolved_at = datetime.now(timezone.utc)
        return appr

    def validate_token(self, approval_id: str, token: str) -> bool:
        appr = self._approvals.get(approval_id)
        if not appr:
            return False
        return appr.is_valid and appr.token == token
