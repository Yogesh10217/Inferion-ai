"""
Tests for Execution Simulator
"""

from app.planning.execution_plan import ExecutionPlan
from app.simulation.simulator import ExecutionSimulator


def test_simulate_plan():
    plan = ExecutionPlan(goal_id="g1", title="Sim Plan", estimated_duration_seconds=20.0, estimated_cost=0.05)
    sim = ExecutionSimulator()
    res = sim.simulate_plan(plan)

    assert res["status"] == "simulated"
    assert "optimistic" in res["scenarios"]
    assert "expected" in res["scenarios"]
    assert "pessimistic" in res["scenarios"]
