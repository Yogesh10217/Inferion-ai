"""
Tests for Workflow Recovery, Rollback, Replay, and Fork
"""

import pytest
from app.workflows.checkpoint import CheckpointManager
from app.workflows.recovery import WorkflowRecoveryManager


def test_rollback_and_fork():
    chk_mgr = CheckpointManager()
    chk = chk_mgr.save_checkpoint(
        run_id="run_orig",
        current_node_id="step_2",
        completed_nodes=["step_1", "step_2"],
        variables={"val": 42},
        memory={},
        agent_outputs={},
        tool_outputs={},
    )

    rec_mgr = WorkflowRecoveryManager(chk_mgr)
    target_chk, restored_ctx = rec_mgr.rollback("run_orig", chk.checkpoint_id)
    assert target_chk.checkpoint_id == chk.checkpoint_id
    assert restored_ctx["variables"]["val"] == 42
    assert restored_ctx["is_recovery"] is True

    # Fork
    new_run_id, new_ctx = rec_mgr.fork("run_orig", chk.checkpoint_id)
    assert new_run_id != "run_orig"
    assert new_ctx["parent_run_id"] == "run_orig"
    assert chk_mgr.get_latest_checkpoint(new_run_id).current_node_id == "step_2"
