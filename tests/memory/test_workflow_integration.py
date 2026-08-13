"""
Tests for Workflow Engine (Phase 5.2) & Memory Integration
"""

from app.memory.memory_manager import MemoryManager


def test_workflow_memory_checkpoint_and_session():
    mm = MemoryManager()
    sess = mm.service.session_tier.create_session("wf_run_101", {"workflow_id": "wf_code_review", "current_step": "analyze"})

    assert sess.context_data["current_step"] == "analyze"

    mm.service.episodic_tier.record_episode(
        episode_type="workflow_run",
        source_id="wf_run_101",
        summary="Completed code review workflow step analyze",
        details={"completed_nodes": ["start", "analyze"]}
    )

    episodes = mm.service.episodic_tier.search_episodes("code review", episode_type="workflow_run")
    assert len(episodes) == 1
    assert episodes[0].source_id == "wf_run_101"
