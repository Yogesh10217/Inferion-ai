"""Unit tests for ExecutionRouter strategies."""

from app.orchestration.routing import ExecutionRouter, RoutingStrategy


def test_routing_strategies():
    router = ExecutionRouter()

    # COST_AWARE strategy with low budget -> WORKER
    dec_cost = router.route_task("summarize_text", strategy=RoutingStrategy.COST_AWARE, max_budget=0.20)
    assert dec_cost.target_type == "WORKER"
    assert dec_cost.estimated_cost < 0.50

    # Elevated risk score -> HUMAN_TASK
    dec_risk = router.route_task("deploy_prod", risk_score=85.0)
    assert dec_risk.target_type == "HUMAN_TASK"
