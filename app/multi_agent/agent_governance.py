"""
Governance and Security Engine for Autonomous Multi-Agent Teams
"""

import logging
from typing import Dict, Any, List, Optional
from app.multi_agent.agent_team import AgentTeam, TeamExecutionContext
from app.multi_agent.agent_profile import AgentProfile
from app.multi_agent.exceptions import RolePermissionDenied

logger = logging.getLogger(__name__)


class AgentGovernanceEngine:
    """Enforces multi-tenant boundaries, RBAC permissions, tool restrictions, and budget policies."""

    @staticmethod
    def validate_team_execution(team: AgentTeam, context: TeamExecutionContext, estimated_cost: float = 0.0) -> None:
        # 1. Multi-tenant Isolation Check
        if team.config.tenant_id not in (context.tenant_id, "global", "default_tenant"):
            raise RolePermissionDenied(f"Tenant isolation violation: Team tenant '{team.config.tenant_id}' != Context tenant '{context.tenant_id}'")

        # 2. RBAC Scope Validation
        if context.user_role != "admin" and "admin" not in context.user_scopes:
            if "team:run" not in context.user_scopes and "tools:execute" not in context.user_scopes:
                raise RolePermissionDenied(f"User '{context.user_id}' lacks required 'team:run' scope for team execution")

        # 3. Budget Limits Check
        if estimated_cost > team.config.budget_dollars:
            raise RolePermissionDenied(f"Budget limit exceeded: estimated cost ${estimated_cost:.4f} > team budget ${team.config.budget_dollars:.4f}")

    @staticmethod
    def validate_agent_action(profile: AgentProfile, action_permission: str) -> None:
        """Validate individual agent role permission before executing action."""
        if action_permission not in profile.role.permissions and "admin" not in profile.role.permissions:
            raise RolePermissionDenied(f"Agent '{profile.name}' with role '{profile.role.name}' lacks permission '{action_permission}'")
