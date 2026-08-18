"""
Tests for Shared Memory Integration (Phase 5.3)
"""

import pytest
from app.multi_agent.shared_memory import SharedMemoryManager


def test_shared_memory_store_and_list():
    mgr = SharedMemoryManager()
    rec = mgr.store_team_memory(
        content="Shared team decision on API design",
        tenant_id="tenant_a",
        organization_id="org_a",
        workspace_id="ws_a",
        team_id="team_engineering",
        author_id="lead_1",
    )

    assert rec.memory_id is not None
    assert "Shared team decision" in rec.content

    memories = mgr.list_team_memories("org_a", "ws_a", "team_engineering")
    assert len(memories) >= 1
    assert memories[0].memory_id == rec.memory_id
