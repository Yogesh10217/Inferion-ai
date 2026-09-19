"""
Agent Team Core Data Structures & Orchestrator Class
"""

import logging
import uuid
from enum import Enum
from typing import Any, Dict, List

from pydantic import BaseModel, Field

from app.multi_agent.agent_profile import AgentProfile
from app.multi_agent.agent_role import AgentRole, RoleType

logger = logging.getLogger(__name__)


class TeamType(str, Enum):
    RESEARCH = "research"
    ENGINEERING = "engineering"
    SUPPORT = "support"
    COMPLIANCE = "compliance"
    ANALYSIS = "analysis"
    CUSTOM = "custom"


class TeamMember(BaseModel):
    member_id: str = Field(default_factory=lambda: f"mbr_{uuid.uuid4().hex[:8]}")
    profile: AgentProfile
    is_active: bool = True
    assigned_tasks_count: int = 0


class TeamConfiguration(BaseModel):
    team_type: TeamType = TeamType.CUSTOM
    name: str
    description: str = ""
    tenant_id: str = "default_tenant"
    organization_id: str = "default_org"
    workspace_id: str = "default_workspace"
    max_concurrent_agents: int = 10
    budget_dollars: float = 10.0
    timeout_seconds: float = 300.0


class TeamExecutionContext(BaseModel):
    execution_id: str = Field(default_factory=lambda: f"team_exec_{uuid.uuid4().hex[:12]}")
    team_id: str
    goal: str
    tenant_id: str = "default_tenant"
    organization_id: str = "default_org"
    workspace_id: str = "default_workspace"
    user_id: str = "anonymous"
    user_role: str = "user"
    user_scopes: List[str] = Field(default_factory=lambda: ["tools:execute", "team:run"])
    initial_inputs: Dict[str, Any] = Field(default_factory=dict)
    shared_variables: Dict[str, Any] = Field(default_factory=dict)
    execution_history: List[Dict[str, Any]] = Field(default_factory=list)


class AgentTeam:
    """Production-grade Multi-Agent Team managing member roles, task delegation, and execution."""

    def __init__(self, team_id: str, config: TeamConfiguration):
        self.team_id = team_id
        self.config = config
        self.members: Dict[str, TeamMember] = {}
        self.status = "created"

    def add_member(self, profile: AgentProfile) -> TeamMember:
        member = TeamMember(profile=profile)
        self.members[profile.agent_id] = member
        logger.info(f"Added member '{profile.name}' ({profile.role.role_type.value}) to team '{self.team_id}'")
        return member

    def remove_member(self, agent_id: str) -> bool:
        if agent_id in self.members:
            del self.members[agent_id]
            logger.info(f"Removed member '{agent_id}' from team '{self.team_id}'")
            return True
        return False

    def get_members_by_role(self, role_type: RoleType) -> List[TeamMember]:
        return [m for m in self.members.values() if m.profile.role.role_type == role_type]

    def list_members(self) -> List[TeamMember]:
        return list(self.members.values())

    @staticmethod
    def create_preset_team(team_type: TeamType, name: str, tenant_id: str = "default_tenant") -> "AgentTeam":
        tid = f"team_{uuid.uuid4().hex[:10]}"
        config = TeamConfiguration(team_type=team_type, name=name, tenant_id=tenant_id)
        team = AgentTeam(tid, config)

        if team_type == TeamType.RESEARCH:
            team.add_member(AgentProfile(name="Lead Researcher", role=AgentRole.get_preset_role(RoleType.MANAGER)))
            team.add_member(AgentProfile(name="Web Searcher", role=AgentRole.get_preset_role(RoleType.RESEARCHER)))
            team.add_member(AgentProfile(name="Synthesizer", role=AgentRole.get_preset_role(RoleType.ANALYST)))
        elif team_type == TeamType.ENGINEERING:
            team.add_member(AgentProfile(name="Engineering Lead", role=AgentRole.get_preset_role(RoleType.MANAGER)))
            team.add_member(AgentProfile(name="Backend Dev", role=AgentRole.get_preset_role(RoleType.DEVELOPER)))
            team.add_member(AgentProfile(name="Code Reviewer", role=AgentRole.get_preset_role(RoleType.REVIEWER)))
            team.add_member(AgentProfile(name="QA Engineer", role=AgentRole.get_preset_role(RoleType.QA)))
        elif team_type == TeamType.COMPLIANCE:
            team.add_member(
                AgentProfile(name="Compliance Lead", role=AgentRole.get_preset_role(RoleType.COMPLIANCE_OFFICER))
            )
            team.add_member(AgentProfile(name="Auditor", role=AgentRole.get_preset_role(RoleType.REVIEWER)))
        else:  # Support / Analysis / Custom
            team.add_member(AgentProfile(name="Team Lead", role=AgentRole.get_preset_role(RoleType.MANAGER)))
            team.add_member(AgentProfile(name="Primary Worker", role=AgentRole.get_preset_role(RoleType.EXECUTOR)))

        return team
