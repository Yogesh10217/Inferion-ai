"""
Tests for Session Memory (Tier 5)
"""

from app.memory.session_memory import SessionMemory


def test_session_memory_lifecycle():
    sm = SessionMemory()
    sess = sm.create_session("sess_001", {"project": "LLM Engine", "task": "Memory Implementation"}, ttl_seconds=3600.0)

    assert sess.session_id == "sess_001"
    assert sess.is_expired() is False

    updated = sm.update_session("sess_001", {"step": 2})
    assert updated.context_data["step"] == 2

    recovered = sm.recover_session("sess_001")
    assert recovered["project"] == "LLM Engine"

    assert sm.expire_session("sess_001") is True
    assert sm.get_session("sess_001") is None
