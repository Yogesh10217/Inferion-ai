"""
Tests for Episodic Memory (Tier 6)
"""

import pytest
from app.memory.episodic_memory import EpisodicMemory


def test_episodic_memory_record_and_search():
    em = EpisodicMemory()
    ep1 = em.record_episode("agent_run", "agent_1", "Completed code review task successfully", {"duration_ms": 120})
    ep2 = em.record_episode("workflow_run", "wf_1", "Executed multi-step deployment pipeline", {"status": "success"})

    assert ep1.episode_id is not None
    assert ep1.episode_type == "agent_run"

    searched = em.search_episodes("code review", episode_type="agent_run")
    assert len(searched) == 1
    assert searched[0].source_id == "agent_1"

    summary = em.summarize_episode(ep1.episode_id)
    assert "agent_1" in summary


def test_episodic_memory_missing_raises_keyerror():
    em = EpisodicMemory()
    with pytest.raises(KeyError):
        em.retrieve_episode("ep_invalid")
