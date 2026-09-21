"""
Tests for Agent Handoff Subsystem
"""

import pytest

from app.multi_agent.agent_handoff import AgentHandoffManager
from app.multi_agent.exceptions import HandoffError


def test_agent_handoff_preserves_context():
    mgr = AgentHandoffManager()
    state = mgr.perform_handoff(
        from_agent_id="agent_1",
        to_agent_id="agent_2",
        execution_state={"step": 2, "plan": "active"},
        memory_snapshot={"context": "previous facts"},
    )

    assert state.from_agent_id == "agent_1"
    assert state.to_agent_id == "agent_2"
    assert state.execution_state["step"] == 2
    assert state.memory_snapshot["context"] == "previous facts"

    last = mgr.get_last_handoff("agent_2")
    assert last.handoff_id == state.handoff_id


def test_handoff_to_self_raises():
    mgr = AgentHandoffManager()
    with pytest.raises(HandoffError):
        mgr.perform_handoff("agent_1", "agent_1", {})
