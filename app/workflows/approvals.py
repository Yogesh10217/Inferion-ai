"""
Human Approval System: Requests, Queues, Audit Logging & Governance
"""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional


class ApprovalDecision(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    CHANGES_REQUESTED = "CHANGES_REQUESTED"
    TIMED_OUT = "TIMED_OUT"
    ESCALATED = "ESCALATED"


class ApprovalRequest:
    """Represents a human approval request paused during workflow execution."""

    def __init__(
        self,
        run_id: str,
        node_id: str,
        workflow_id: str,
        prompt: str = "Approval required to proceed",
        approver_role: str = "approver",
        timeout_seconds: Optional[float] = None,
        request_id: Optional[str] = None,
        created_at: Optional[str] = None,
    ):
        self.request_id = request_id or f"appr_{uuid.uuid4().hex[:12]}"
        self.run_id = run_id
        self.node_id = node_id
        self.workflow_id = workflow_id
        self.prompt = prompt
        self.approver_role = approver_role
        self.timeout_seconds = timeout_seconds

        self.status: ApprovalDecision = ApprovalDecision.PENDING
        self.decision: Optional[str] = None
        self.feedback: Optional[str] = None
        self.decided_by: Optional[str] = None
        self.created_at = created_at or datetime.now(timezone.utc).isoformat()
        self.decided_at: Optional[str] = None
        self.audit_log: List[Dict[str, Any]] = [
            {"event": "created", "timestamp": self.created_at, "role": approver_role}
        ]

    def record_decision(
        self, decision: ApprovalDecision, decided_by: str = "user", feedback: Optional[str] = None
    ) -> None:
        """Record an approval, rejection, or change request decision."""
        self.status = decision
        self.decision = decision.value
        self.decided_by = decided_by
        self.feedback = feedback
        self.decided_at = datetime.now(timezone.utc).isoformat()
        self.audit_log.append(
            {
                "event": decision.value.lower(),
                "decided_by": decided_by,
                "feedback": feedback,
                "timestamp": self.decided_at,
            }
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "request_id": self.request_id,
            "run_id": self.run_id,
            "node_id": self.node_id,
            "workflow_id": self.workflow_id,
            "prompt": self.prompt,
            "approver_role": self.approver_role,
            "status": self.status.value,
            "decision": self.decision,
            "feedback": self.feedback,
            "decided_by": self.decided_by,
            "created_at": self.created_at,
            "decided_at": self.decided_at,
            "audit_log": self.audit_log,
        }


class ApprovalManager:
    """Manages pending human approval queues and records audit decisions."""

    def __init__(self):
        self._requests: Dict[str, ApprovalRequest] = {}  # request_id -> ApprovalRequest
        self._run_index: Dict[str, List[str]] = {}  # run_id -> list of request_ids

    def create_request(
        self,
        run_id: str,
        node_id: str,
        workflow_id: str,
        prompt: str = "Approval required",
        approver_role: str = "approver",
        timeout_seconds: Optional[float] = None,
    ) -> ApprovalRequest:
        req = ApprovalRequest(
            run_id=run_id,
            node_id=node_id,
            workflow_id=workflow_id,
            prompt=prompt,
            approver_role=approver_role,
            timeout_seconds=timeout_seconds,
        )
        self._requests[req.request_id] = req
        if run_id not in self._run_index:
            self._run_index[run_id] = []
        self._run_index[run_id].append(req.request_id)
        return req

    def get_request(self, request_id: str) -> Optional[ApprovalRequest]:
        return self._requests.get(request_id)

    def get_pending_request_for_run(self, run_id: str) -> Optional[ApprovalRequest]:
        req_ids = self._run_index.get(run_id, [])
        for r_id in reversed(req_ids):
            req = self._requests.get(r_id)
            if req and req.status == ApprovalDecision.PENDING:
                return req
        return None

    def approve(self, request_id: str, decided_by: str = "user", feedback: Optional[str] = None) -> ApprovalRequest:
        req = self._requests.get(request_id)
        if not req:
            raise KeyError(f"Approval request '{request_id}' not found")
        req.record_decision(ApprovalDecision.APPROVED, decided_by=decided_by, feedback=feedback)
        return req

    def reject(self, request_id: str, decided_by: str = "user", feedback: Optional[str] = None) -> ApprovalRequest:
        req = self._requests.get(request_id)
        if not req:
            raise KeyError(f"Approval request '{request_id}' not found")
        req.record_decision(ApprovalDecision.REJECTED, decided_by=decided_by, feedback=feedback)
        return req

    def request_changes(
        self, request_id: str, decided_by: str = "user", feedback: Optional[str] = None
    ) -> ApprovalRequest:
        req = self._requests.get(request_id)
        if not req:
            raise KeyError(f"Approval request '{request_id}' not found")
        req.record_decision(ApprovalDecision.CHANGES_REQUESTED, decided_by=decided_by, feedback=feedback)
        return req

    def escalate(self, request_id: str, decided_by: str = "user", feedback: Optional[str] = None) -> ApprovalRequest:
        req = self._requests.get(request_id)
        if not req:
            raise KeyError(f"Approval request '{request_id}' not found")
        req.record_decision(ApprovalDecision.ESCALATED, decided_by=decided_by, feedback=feedback)
        return req

    def list_requests(self, status: Optional[str] = None) -> List[ApprovalRequest]:
        if status:
            return [req for req in self._requests.values() if req.status.value == status]
        return list(self._requests.values())
