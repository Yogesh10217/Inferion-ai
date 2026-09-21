"""
Tests for Checkpoint Manager
"""

from app.autonomy.checkpoint_manager import CheckpointManager


def test_checkpoint_save_and_rollback():
    mgr = CheckpointManager()
    mgr.save_checkpoint("exec_1", step_number=1, state_data={"step": 1})
    snap2 = mgr.save_checkpoint("exec_1", step_number=2, state_data={"step": 2})

    latest = mgr.get_latest_checkpoint("exec_1")
    assert latest.checkpoint_id == snap2.checkpoint_id

    rolled = mgr.rollback_to_checkpoint("exec_1", step_number=1)
    assert rolled.step_number == 1
