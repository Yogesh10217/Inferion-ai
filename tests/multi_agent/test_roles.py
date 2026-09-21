"""
Tests for Agent Roles & Presets
"""

from app.multi_agent.agent_role import AgentRole, RoleType


def test_preset_roles():
    mgr = AgentRole.get_preset_role(RoleType.MANAGER)
    assert mgr.role_type == RoleType.MANAGER
    assert "team:manage" in mgr.permissions

    dev = AgentRole.get_preset_role(RoleType.DEVELOPER)
    assert dev.role_type == RoleType.DEVELOPER
    assert "write_code" in dev.capabilities

    qa = AgentRole.get_preset_role(RoleType.QA)
    assert qa.role_type == RoleType.QA
    assert "test_execution" in qa.capabilities
