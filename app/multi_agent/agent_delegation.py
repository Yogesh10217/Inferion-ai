"""
Task Delegation Engine and Routing Strategies
"""

import time
import logging
from typing import Dict, Any, List, Optional
from enum import Enum
from pydantic import BaseModel, Field

from app.multi_agent.agent_team import AgentTeam, TeamMember
from app.multi_agent.agent_role import RoleType
from app.multi_agent.exceptions import DelegationError

logger = logging.getLogger(__name__)


class DelegationStrategy(str, Enum):
    CAPABILITY_MATCH = "capability_match"
    LOAD_BALANCING = "load_balancing"
    PRIORITY_ROUTING = "priority_routing"
    SKILL_BASED = "skill_based"


class DelegationPolicy(BaseModel):
    policy_name: str = "default_delegation"
    strategy: DelegationStrategy = DelegationStrategy.CAPABILITY_MATCH
    max_delegation_depth: int = 5
    allow_cross_role_delegation: bool = True


class TaskDelegator:
    """Delegator assigning tasks dynamically across team members."""

    def __init__(self, team: AgentTeam, policy: Optional[DelegationPolicy] = None):
        self.team = team
        self.policy = policy or DelegationPolicy()
        self.delegation_history: List[Dict[str, Any]] = []

    def delegate_task(
        self,
        task_prompt: str,
        delegator_id: str,
        required_skills: Optional[List[str]] = None,
        priority: int = 1,
    ) -> TeamMember:
        """Assign task to the optimal team member based on policy strategy."""
        members = [m for m in self.team.list_members() if m.is_active and m.profile.agent_id != delegator_id]

        if not members:
            # Fallback to any member including delegator if team of size 1
            all_m = self.team.list_members()
            if not all_m:
                raise DelegationError(f"No active members available in team '{self.team.team_id}' for delegation")
            members = all_m

        selected: Optional[TeamMember] = None

        if self.policy.strategy == DelegationStrategy.SKILL_BASED and required_skills:
            for m in members:
                if any(skill in m.profile.capabilities for skill in required_skills):
                    selected = m
                    break

        if not selected and self.policy.strategy == DelegationStrategy.LOAD_BALANCING:
            selected = min(members, key=lambda m: m.assigned_tasks_count)

        if not selected:
            # Default capability or first active member match
            selected = members[0]

        selected.assigned_tasks_count += 1
        record = {
            "timestamp": time.time(),
            "delegator_id": delegator_id,
            "assigned_to": selected.profile.agent_id,
            "task_prompt": task_prompt,
            "strategy": self.policy.strategy.value,
        }
        self.delegation_history.append(record)
        logger.info(f"Delegated task '{task_prompt[:30]}...' from '{delegator_id}' -> '{selected.profile.agent_id}'")
        return selected
