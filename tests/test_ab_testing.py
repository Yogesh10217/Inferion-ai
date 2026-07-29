import pytest
from app.routing.routing_rules import RuleEngine, RoutingRule
from app.routing.routing_context import RoutingContext


def test_routing_rules_evaluation():
    engine = RuleEngine()
    rule = RoutingRule(
        name="ab_test_experimental",
        priority=200,
        condition=lambda ctx: ctx.request_metadata.get("experiment") == "v2",
        target_provider="experimental_provider",
    )
    engine.add_rule(rule)

    ctx = RoutingContext(request_metadata={"experiment": "v2"})
    directives = engine.evaluate(ctx)
    assert directives is not None
    assert directives["matched_rule"] == "ab_test_experimental"
    assert directives["target_provider"] == "experimental_provider"
