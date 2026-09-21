"""
Tests for Optimization Engine
"""

from app.learning.optimization_engine import OptimizationEngine


def test_optimize_plan_workflow():
    engine = OptimizationEngine()
    rec = engine.optimize_plan_workflow("plan_1", [{"node_id": "n1"}, {"node_id": "n2"}])

    assert rec.recommendation_id.startswith("opt_")
    assert rec.status == "pending_approval"
    assert len(engine.list_recommendations()) == 1
