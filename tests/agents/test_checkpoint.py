"""
Checkpoint Unit Tests
"""

from app.agents.agent_state import AgentState, AgentStatus
from app.agents.checkpoint import CheckpointManager


def test_checkpoint_save_and_load():
    manager = CheckpointManager()
    state = AgentState(session_id="sess_123", agent_id="agent_demo", status=AgentStatus.PLANNING)

    name = manager.save_checkpoint("sess_123", state, "cp_step_1")
    assert name == "cp_step_1"

    restored = manager.load_checkpoint("sess_123", "cp_step_1")
    assert restored.session_id == "sess_123"
    assert restored.agent_id == "agent_demo"
    assert restored.status == AgentStatus.PLANNING
