"""
Tests for Execution Plan Model
"""

from app.planning.execution_plan import ExecutionPlan


def test_execution_plan_model():
    plan = ExecutionPlan(goal_id="g1", title="Plan Title", confidence_score=0.95)
    assert plan.goal_id == "g1"
    assert plan.status == "draft"
