"""
Agent Router for Target Resolution & Capability-Based Route Matching
"""

import logging
from typing import Optional

from app.multi_agent.agent_role import RoleType
from app.multi_agent.agent_team import AgentTeam

logger = logging.getLogger(__name__)


class AgentRouter:
    """Routes messages to target agents based on role, capabilities, or workload."""

    def __init__(self, team: AgentTeam):
        self.team = team

    def route_task(self, task_description: str, required_capability: Optional[str] = None) -> Optional[str]:
        """Find best agent_id for a given task description or capability."""
        # 1. Capability match
        if required_capability:
            for member in self.team.list_members():
                if required_capability in member.profile.capabilities:
                    return member.profile.agent_id

        # 2. Role match (prefer EXECUTOR or DEVELOPER for tasks)
        executors = self.team.get_members_by_role(RoleType.EXECUTOR)
        if executors:
            return executors[0].profile.agent_id

        devs = self.team.get_members_by_role(RoleType.DEVELOPER)
        if devs:
            return devs[0].profile.agent_id

        researchers = self.team.get_members_by_role(RoleType.RESEARCHER)
        if researchers:
            return researchers[0].profile.agent_id

        # 3. Fallback to any member
        members = self.team.list_members()
        return members[0].profile.agent_id if members else None
