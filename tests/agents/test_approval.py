"""
Approval Controller Unit Tests
"""

import pytest

from app.agents.agent_state import AgentState, AgentStatus
from app.agents.approval import ApprovalController
from app.agents.exceptions import ApprovalRequiredException


def test_human_approval_flow():
    controller = ApprovalController()
    state = AgentState(session_id="sess_456", agent_id="agent_demo")

    with pytest.raises(ApprovalRequiredException):
        controller.check_approval(
            tool_name="shell_executor",
            tool_args={"command": "ls"},
            required_tools=["shell_executor"],
            session_id="sess_456",
            state=state,
        )

    assert state.status == AgentStatus.AWAITING_APPROVAL

    result = controller.submit_approval("sess_456", approved=True, feedback="Approved by admin")
    assert result["status"] == "APPROVED"
