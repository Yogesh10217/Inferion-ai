"""
Agent Human Approval Controller
"""

import logging
import time
from typing import Any, Dict, Optional

from app.agents.agent_state import AgentState, AgentStatus
from app.agents.exceptions import ApprovalRequiredException

logger = logging.getLogger(__name__)


class ApprovalController:
    def __init__(self):
        self._pending_approvals: Dict[str, Dict[str, Any]] = {}

    def check_approval(
        self,
        tool_name: str,
        tool_args: Dict[str, Any],
        required_tools: list,
        session_id: str,
        state: AgentState
    ) -> None:
        if tool_name in required_tools:
            approval_request = {
                "session_id": session_id,
                "tool_name": tool_name,
                "tool_args": tool_args,
                "requested_at": time.time(),
                "status": "PENDING"
            }
            self._pending_approvals[session_id] = approval_request
            state.status = AgentStatus.AWAITING_APPROVAL
            state.pending_approval = approval_request
            logger.info(f"Tool '{tool_name}' requires approval for session '{session_id}'")
            raise ApprovalRequiredException(
                f"Tool '{tool_name}' requires human approval before execution in session '{session_id}'."
            )

    def submit_approval(self, session_id: str, approved: bool, feedback: Optional[str] = None) -> Dict[str, Any]:
        req = self._pending_approvals.get(session_id)
        if not req:
            raise ValueError(f"No pending approval request found for session '{session_id}'")

        req["status"] = "APPROVED" if approved else "REJECTED"
        req["feedback"] = feedback
        req["responded_at"] = time.time()
        del self._pending_approvals[session_id]
        return req
