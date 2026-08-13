"""
Tests for Checkpointing & State Snapshot Management
"""

import pytest
from app.workflows.checkpoint import CheckpointManager, CheckpointNotFoundError


def test_checkpoint_saving_and_retrieval():
    mgr = CheckpointManager()
    chk = mgr.save_checkpoint(
        run_id="run_1",
        current_node_id="a1",
        completed_nodes=["START", "a1"],
        variables={"score": 100},
        memory={"ctx": "mem"},
        agent_outputs={"a1": "done"},
        tool_outputs={},
    )

    assert chk.checkpoint_id.startswith("chk_")
    latest = mgr.get_latest_checkpoint("run_1")
    assert latest.checkpoint_id == chk.checkpoint_id
    assert latest.current_node_id == "a1"
    assert latest.variables["score"] == 100

    fetched = mgr.get_checkpoint("run_1", chk.checkpoint_id)
    assert fetched.checkpoint_id == chk.checkpoint_id


def test_missing_checkpoint_raises_error():
    mgr = CheckpointManager()
    with pytest.raises(CheckpointNotFoundError):
        mgr.get_latest_checkpoint("non_existent_run")
