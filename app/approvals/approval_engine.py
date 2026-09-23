"""
Human Approval Workflow Engine
"""

import logging
import time
from typing import Any, Dict, List, Optional

from app.approvals.approval_policies import RiskLevel
from app.approvals.approval_request import ApprovalRequest, ApprovalStatus

logger = logging.getLogger(__name__)


class ApprovalEngine:
    """Manages human-in-the-loop approval workflows for high-risk autonomous actions."""

    def __init__(self):
        self._requests: Dict[str, ApprovalRequest] = {}

    def request_approval(
        self,
        execution_id: str,
        action_type: str,
        risk_level: RiskLevel = RiskLevel.MEDIUM,
        requester: str = "autonomous_agent",
        tenant_id: str = "default_tenant",
        payload: Optional[Dict[str, Any]] = None,
    ) -> ApprovalRequest:
        req = ApprovalRequest(
            execution_id=execution_id,
            tenant_id=tenant_id,
            requester=requester,
            risk_level=risk_level,
            action_type=action_type,
            payload=payload or {},
        )
        self._requests[req.request_id] = req
        logger.info(
            f"[APPROVAL ENGINE] Created approval request '{req.request_id}' for action '{action_type}' (risk: {risk_level.value})"
        )
        return req

    def create_approval_request(
        self,
        requester: str = "autonomous_agent",
        action: str = "action",
        context: Optional[Dict[str, Any]] = None,
        tenant_id: str = "default_tenant",
        risk_level: RiskLevel = RiskLevel.HIGH,
    ) -> ApprovalRequest:
        return self.request_approval(
            execution_id=f"exec_{time.time()}",
            action_type=action,
            risk_level=risk_level,
            requester=requester,
            tenant_id=tenant_id,
            payload=context,
        )

    def approve(self, request_id: str, approver_id: str) -> ApprovalRequest:
        if request_id not in self._requests:
            raise ValueError(f"Approval request '{request_id}' not found")
        req = self._requests[request_id]
        req.status = ApprovalStatus.APPROVED
        req.approver = approver_id
        req.resolved_at = time.time()
        logger.info(f"[APPROVAL ENGINE] Request '{request_id}' APPROVED by '{approver_id}'")
        return req

    def reject(self, request_id: str, approver_id: str, reason: str = "") -> ApprovalRequest:
        if request_id not in self._requests:
            raise ValueError(f"Approval request '{request_id}' not found")
        req = self._requests[request_id]
        req.status = ApprovalStatus.REJECTED
        req.approver = approver_id
        req.resolved_at = time.time()
        logger.info(f"[APPROVAL ENGINE] Request '{request_id}' REJECTED by '{approver_id}' (reason: {reason})")
        return req

    def expire(self, request_id: str) -> ApprovalRequest:
        if request_id not in self._requests:
            raise ValueError(f"Approval request '{request_id}' not found")
        req = self._requests[request_id]
        req.status = ApprovalStatus.EXPIRED
        req.resolved_at = time.time()
        return req

    def escalate(self, request_id: str) -> ApprovalRequest:
        if request_id not in self._requests:
            raise ValueError(f"Approval request '{request_id}' not found")
        req = self._requests[request_id]
        req.status = ApprovalStatus.ESCALATED
        return req

    def get_pending_requests(self, tenant_id: str = "default_tenant") -> List[ApprovalRequest]:
        return [
            r
            for r in self._requests.values()
            if r.status == ApprovalStatus.PENDING and r.tenant_id in (tenant_id, "global", "default_tenant")
        ]
