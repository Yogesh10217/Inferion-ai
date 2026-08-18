"""
Tests for Blackboard Shared Workspace
"""

import pytest
from app.multi_agent.agent_blackboard import Blackboard


def test_blackboard_write_read_list():
    bb = Blackboard()
    bb.write(
        key="architecture_plan",
        value={"style": "microservices"},
        author_id="dev_1",
        tenant_id="tenant_x",
        workspace_id="ws_1",
        team_id="team_1",
        category="plan",
    )

    entry = bb.read("architecture_plan", tenant_id="tenant_x", workspace_id="ws_1", team_id="team_1")
    assert entry is not None
    assert entry.value["style"] == "microservices"
    assert entry.author_id == "dev_1"

    # Multi-tenant isolation check
    entry_isolated = bb.read("architecture_plan", tenant_id="tenant_other", workspace_id="ws_1", team_id="team_1")
    assert entry_isolated is None
