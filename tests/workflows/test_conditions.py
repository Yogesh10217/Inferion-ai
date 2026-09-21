"""
Tests for Conditional Edge Evaluator & Branch Routing
"""

from app.workflows.conditions import ConditionalExecutor
from app.workflows.edge import Edge


def test_edge_condition_evaluation():
    edge_true = Edge("a", "b", condition="score > 80")
    edge_false = Edge("a", "c", condition="score <= 80")

    context_high = {"variables": {"score": 95}}
    context_low = {"variables": {"score": 50}}

    assert edge_true.evaluate_condition(context_high) is True
    assert edge_false.evaluate_condition(context_high) is False

    assert edge_true.evaluate_condition(context_low) is False
    assert edge_false.evaluate_condition(context_low) is True


def test_conditional_executor_select_active_edges():
    e1 = Edge("src", "t1", condition="score > 90")
    e2 = Edge("src", "t2", condition="score <= 90")

    context = {"variables": {"score": 95}}
    active = ConditionalExecutor.select_active_edges([e1, e2], context)
    assert len(active) == 1
    assert active[0].target_node == "t1"
