"""
Tests for Multi-Tenant Isolation & Security Governance in Planning
"""

import pytest

from app.planning.exceptions import ResourcePlanningError
from app.planning.execution_plan import ExecutionPlan
from app.planning.governance import PlanningGovernanceEngine


def test_tenant_isolation_in_planning():
    plan = ExecutionPlan(goal_id="g1", title="Isolated Plan", tenant_id="tenant_x")

    with pytest.raises(ResourcePlanningError) as exc:
        PlanningGovernanceEngine.validate_plan_execution(plan, tenant_id="tenant_y")

    assert "Tenant isolation violation" in str(exc.value)


def test_budget_limit_in_planning():
    plan = ExecutionPlan(goal_id="g1", title="Expensive Plan", tenant_id="tenant_x", estimated_cost=100.0)

    with pytest.raises(ResourcePlanningError) as exc:
        PlanningGovernanceEngine.validate_plan_execution(plan, tenant_id="tenant_x", workspace_budget_dollars=10.0)

    assert "Workspace budget exceeded" in str(exc.value)
