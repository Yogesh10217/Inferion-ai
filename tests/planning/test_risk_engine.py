"""
Tests for Risk Analysis Engine
"""

import pytest
from app.planning.execution_plan import ExecutionPlan
from app.simulation.risk_engine import RiskEngine


def test_analyze_plan_risks():
    plan = ExecutionPlan(goal_id="g1", title="High Cost Plan", estimated_cost=15.0)
    risks = RiskEngine.analyze_plan_risks(plan)

    assert len(risks) >= 1
    assert any(r.risk_id == "risk_cost_overrun" for r in risks)
