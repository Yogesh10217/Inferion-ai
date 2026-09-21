from app.routing.routing_context import RoutingContext
from app.routing.routing_rules import RoutingRule, RuleEngine


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


def test_routing_rules_fallback_when_unmatched():
    engine = RuleEngine()
    rule = RoutingRule(
        name="ab_test_experimental",
        priority=200,
        condition=lambda ctx: ctx.request_metadata.get("experiment") == "v2",
        target_provider="experimental_provider",
    )
    engine.add_rule(rule)

    # Request without experiment tag
    ctx = RoutingContext(request_metadata={"experiment": "control"})
    directives = engine.evaluate(ctx)
    assert directives is None


def test_routing_rule_priority_ordering():
    engine = RuleEngine()
    low_rule = RoutingRule(
        name="low_priority",
        priority=10,
        condition=lambda ctx: True,
        target_provider="default_provider",
    )
    high_rule = RoutingRule(
        name="high_priority",
        priority=100,
        condition=lambda ctx: True,
        target_provider="vip_provider",
    )
    engine.add_rule(low_rule)
    engine.add_rule(high_rule)

    ctx = RoutingContext()
    directives = engine.evaluate(ctx)
    assert directives["matched_rule"] == "high_priority"
    assert directives["target_provider"] == "vip_provider"
