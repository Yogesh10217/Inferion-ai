"""
Tests for Security & Permission Engine
"""

import pytest
from app.tools.tool import BaseTool, ToolMetadata, ToolCapability
from app.tools.tool_context import ToolContext
from app.tools.tool_permissions import ToolPermissionEngine
from app.tools.tool_policies import ToolPolicy, PolicyRule, PolicyEffect
from app.tools.exceptions import ToolPermissionDenied, ToolApprovalRequiredException
from app.tools.tool_result import ToolResult, ToolExecutionStatus


class PermTestTool(BaseTool):
    def __init__(self, tenant_id: str = "tenant_a", scopes=None, cost: float = 0.05, requires_approval: bool = False):
        meta = ToolMetadata(
            name="perm_tool",
            description="Permission test tool",
            tenant_id=tenant_id,
            scopes=scopes or ["tools:execute"],
            cost_estimate=cost,
            requires_approval=requires_approval,
            capabilities=[ToolCapability.HIGH_RISK] if requires_approval else [ToolCapability.READ],
        )
        super().__init__(meta)

    async def execute_async(self, parameters: dict, context: ToolContext) -> ToolResult:
        return ToolResult(execution_id=context.execution_id, tool_name=self.name, status=ToolExecutionStatus.SUCCESS)


def test_cross_tenant_access_blocked():
    engine = ToolPermissionEngine()
    tool = PermTestTool(tenant_id="tenant_a")
    ctx = ToolContext(tenant_id="tenant_b")

    with pytest.raises(ToolPermissionDenied) as exc:
        engine.validate_execution(tool, ctx)
    assert "Cross-tenant access denied" in str(exc.value)


def test_rbac_scope_check():
    engine = ToolPermissionEngine()
    tool = PermTestTool(tenant_id="tenant_a", scopes=["admin:write"])
    ctx = ToolContext(tenant_id="tenant_a", user_role="user", user_scopes=["tools:read"])

    with pytest.raises(ToolPermissionDenied) as exc:
        engine.validate_execution(tool, ctx)
    assert "RBAC scope check failed" in str(exc.value)


def test_budget_limit_exceeded():
    engine = ToolPermissionEngine()
    tool = PermTestTool(tenant_id="tenant_a", cost=10.0)
    ctx = ToolContext(tenant_id="tenant_a", budget_limit=5.0)

    with pytest.raises(ToolPermissionDenied) as exc:
        engine.validate_execution(tool, ctx, cost_estimate=10.0)
    assert "Cost limit exceeded" in str(exc.value)


def test_policy_rule_deny_and_approval():
    engine = ToolPermissionEngine()
    policy = ToolPolicy(
        policy_id="pol_1",
        tenant_id="tenant_a",
        name="Strict Policy",
        rules=[
            PolicyRule(rule_id="r1", effect=PolicyEffect.DENY, target_tools=["perm_tool"]),
        ],
    )
    engine.add_policy(policy)
    tool = PermTestTool(tenant_id="tenant_a")
    ctx = ToolContext(tenant_id="tenant_a")

    with pytest.raises(ToolPermissionDenied) as exc:
        engine.validate_execution(tool, ctx)
    assert "explicitly denied" in str(exc.value)


def test_high_risk_approval_required():
    engine = ToolPermissionEngine()
    tool = PermTestTool(tenant_id="tenant_a", requires_approval=True)
    ctx = ToolContext(tenant_id="tenant_a")

    with pytest.raises(ToolApprovalRequiredException) as exc:
        engine.validate_execution(tool, ctx)
    assert "requires approval" in str(exc.value)
