"""
Tests for AgentTeam and Team Lifecycle Subsystem
"""

import pytest
from app.multi_agent.agent_team import AgentTeam, TeamType, TeamConfiguration
from app.multi_agent.agent_profile import AgentProfile
from app.multi_agent.agent_role import AgentRole, RoleType


def test_create_preset_teams():
    team = AgentTeam.create_preset_team(TeamType.ENGINEERING, "Dev Team", tenant_id="org_alpha")
    assert team.config.name == "Dev Team"
    assert len(team.list_members()) == 4

    managers = team.get_members_by_role(RoleType.MANAGER)
    assert len(managers) == 1
    assert managers[0].profile.role.role_type == RoleType.MANAGER


def test_add_remove_team_members():
    team = AgentTeam("team_123", TeamConfiguration(name="Custom Team"))
    prof = AgentProfile(name="Tester Agent", role=AgentRole.get_preset_role(RoleType.QA))

    mbr = team.add_member(prof)
    assert len(team.list_members()) == 1
    assert mbr.profile.name == "Tester Agent"

    removed = team.remove_member(prof.agent_id)
    assert removed is True
    assert len(team.list_members()) == 0
