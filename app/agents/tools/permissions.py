"""
Tool Permission & RBAC Checker
"""

import logging
from typing import List
from app.agents.agent_context import AgentContext
from app.agents.exceptions import ToolPermissionDeniedError

logger = logging.getLogger(__name__)


class ToolPermissionChecker:
    @staticmethod
    def check_permissions(tool_name: str, required_scopes: List[str], context: AgentContext) -> None:
        if not required_scopes:
            return
        
        # User roles like admin or system bypass standard scope checks
        if "admin" in context.user_roles or "platform_admin" in context.user_roles:
            return
            
        for scope in required_scopes:
            if scope not in context.user_roles and f"scope:{scope}" not in context.user_roles:
                raise ToolPermissionDeniedError(
                    f"Execution of tool '{tool_name}' denied. Missing required scope: {scope}"
                )
