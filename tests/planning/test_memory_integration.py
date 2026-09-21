"""
Tests for Memory Integration (Phase 5.3)
"""

from app.memory.memory_service import MemoryService


def test_planning_memory_integration():
    svc = MemoryService()
    entry = svc.create_memory_entry(
        "Lesson: use retries for http tool", organization_id="org_a", workspace_id="ws_a", user_id="planner"
    )
    assert entry.memory_id is not None
    assert "use retries" in entry.content
