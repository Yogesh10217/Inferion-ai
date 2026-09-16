"""Runtime approval coordinator for Runtime Intelligence (Phase 5.57)."""

import logging
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

from app.runtime_intelligence.exceptions import (
    CrossTenantRuntimeIntelligenceException,
    RuntimeIntelligenceException,
)

logger = logging.getLogger(__name__)


class RuntimeApprovalCoordinator:
    """Coordinates approval workflows for high-risk runtime actions with expiry and tracking."""

    def __init__(self) -> None:
        self._approvals: Dict[str, Dict[str, Any]] = {}

    def request_approval(
        self,
        tenant_id: str,
        action_name: str,
        risk_level: str = "HIGH",
        reason: str = "High-risk runtime operational change requiring human sign-off",
        ttl_minutes: int = 60,
    ) -> Dict[str, Any]:
        now = datetime.now(timezone.utc)
        approval_id = f"appr_{uuid.uuid4().hex[:12]}"
        req = {
            "approval_id": approval_id,
            "tenant_id": tenant_id,
            "action_name": action_name,
            "risk_level": risk_level,
            "reason": reason,
            "status": "PENDING",
            "requested_at": now.isoformat(),
            "expires_at": (now + timedelta(minutes=ttl_minutes)).isoformat(),
            "decided_by": None,
            "decided_at": None,
            "decision_notes": "",
        }
        self._approvals[approval_id] = req
        logger.info(f"Created RuntimeApproval Request '{approval_id}' for action '{action_name}' (tenant: '{tenant_id}')")
        return req

    def approve(
        self, tenant_id: str, approval_id: str, reviewer_id: str, notes: str = ""
    ) -> Dict[str, Any]:
        req = self._approvals.get(approval_id)
        if not req:
            raise RuntimeIntelligenceException("Approval request not found")
        if req["tenant_id"] != tenant_id:
            raise CrossTenantRuntimeIntelligenceException()

        req["status"] = "APPROVED"
        req["decided_by"] = reviewer_id
        req["decided_at"] = datetime.now(timezone.utc).isoformat()
        req["decision_notes"] = notes
        logger.info(f"Approved runtime action '{req['action_name']}' by '{reviewer_id}' (ID: {approval_id})")
        return req

    def reject(
        self, tenant_id: str, approval_id: str, reviewer_id: str, reason: str = ""
    ) -> Dict[str, Any]:
        req = self._approvals.get(approval_id)
        if not req:
            raise RuntimeIntelligenceException("Approval request not found")
        if req["tenant_id"] != tenant_id:
            raise CrossTenantRuntimeIntelligenceException()

        req["status"] = "REJECTED"
        req["decided_by"] = reviewer_id
        req["decided_at"] = datetime.now(timezone.utc).isoformat()
        req["decision_notes"] = reason
        logger.info(f"Rejected runtime action '{req['action_name']}' by '{reviewer_id}' (ID: {approval_id})")
        return req

    def get_approval(self, tenant_id: str, approval_id: str) -> Optional[Dict[str, Any]]:
        req = self._approvals.get(approval_id)
        if req and req["tenant_id"] != tenant_id:
            raise CrossTenantRuntimeIntelligenceException()
        return req
