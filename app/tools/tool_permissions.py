"""
Security Layer & Tool Permission Engine
"""

import logging
from typing import Dict
from app.tools.tool import BaseTool, ToolCapability
from app.tools.tool_context import ToolContext
from app.tools.tool_policies import ToolPolicy, PolicyEffect

from app.tools.exceptions import ToolPermissionDenied, ToolApprovalRequiredException

logger = logging.getLogger(__name__)


class ToolPermissionEngine:
    """Enforces multi-tenant isolation, RBAC role/scopes, cost limits, and approval policies."""

    def __init__(self):
        self._policies: Dict[str, ToolPolicy] = {}

    def add_policy(self, policy: ToolPolicy) -> None:
        self._policies[policy.policy_id] = policy

    def remove_policy(self, policy_id: str) -> bool:
        return self._policies.pop(policy_id, None) is not None

    def validate_execution(self, tool: BaseTool, context: ToolContext, cost_estimate: float = 0.0) -> None:
        """
        Validates authorization for tool execution against tenant boundaries, RBAC,
        policies, and cost limits.
        """
        # 1. Multi-tenant Isolation Check
        tool_tid = tool.metadata.tenant_id
        ctx_tid = context.tenant_id

        if tool_tid not in (ctx_tid, "global", "default_tenant"):
            logger.warning(f"Cross-tenant access blocked: user tenant '{ctx_tid}' attempted to access tool tenant '{tool_tid}'")
            raise ToolPermissionDenied(f"Cross-tenant access denied: Tool '{tool.name}' belongs to tenant '{tool_tid}'")

        # 2. RBAC Scope Validation
        if context.user_role != "admin" and "admin" not in context.user_scopes:
            req_scopes = tool.metadata.scopes
            if req_scopes:
                if not any(s in context.user_scopes for s in req_scopes):
                    raise ToolPermissionDenied(
                        f"RBAC scope check failed: user lacks required scopes {req_scopes} for tool '{tool.name}'"
                    )

        # 3. Budget / Cost Limit Check
        if context.budget_limit is not None and cost_estimate > context.budget_limit:
            raise ToolPermissionDenied(
                f"Cost limit exceeded: tool cost estimate ${cost_estimate:.4f} exceeds context budget limit ${context.budget_limit:.4f}"
            )

        # 4. Policy Rules Check
        for policy in self._policies.values():
            if not policy.is_active:
                continue
            if policy.tenant_id not in (ctx_tid, "global", "default_tenant"):
                continue

            for rule in policy.rules:
                # Check tool match
                tool_matches = "*" in rule.target_tools or tool.name in rule.target_tools
                cat_matches = not rule.target_categories or tool.metadata.category.value in rule.target_categories

                if tool_matches and cat_matches:
                    # Check max cost per call
                    if rule.max_cost_per_call is not None and cost_estimate > rule.max_cost_per_call:
                        raise ToolPermissionDenied(
                            f"Policy rule '{rule.rule_id}' blocked execution: cost ${cost_estimate:.4f} exceeds policy limit ${rule.max_cost_per_call:.4f}"
                        )

                    if rule.effect == PolicyEffect.DENY:
                        raise ToolPermissionDenied(f"Policy rule '{rule.rule_id}' explicitly denied execution of tool '{tool.name}'")
                    elif rule.effect == PolicyEffect.REQUIRE_APPROVAL:
                        raise ToolApprovalRequiredException(
                            f"Execution of tool '{tool.name}' requires manual approval per policy rule '{rule.rule_id}'",
                            execution_id=context.execution_id,
                            tool_name=tool.name,
                        )

        # 5. Capability / High-Risk Approval Check
        if tool.metadata.requires_approval or ToolCapability.HIGH_RISK in tool.metadata.capabilities:
            if context.metadata.get("approval_status") != "approved":
                raise ToolApprovalRequiredException(
                    f"High-risk action for tool '{tool.name}' requires approval",
                    execution_id=context.execution_id,
                    tool_name=tool.name,
                )
