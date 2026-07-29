import pytest
from app.routing.decision_engine import DecisionEngine
from app.routing.routing_context import RoutingContext
from app.routing.routing_policy import RoutingPolicy
from app.routing.decision_engine_strategy import DecisionEngineRoutingStrategy


def test_decision_engine_pipeline():
    engine = DecisionEngine()
    ctx = RoutingContext(required_capabilities=["chat"])
    selected = engine.decide("gpt-4", ctx)
    assert selected in ["openai_provider", "anthropic_provider", "mock_provider"]
    assert "final_decision" in ctx.decision_explanation
    assert len(ctx.get_full_trace()) > 0


def test_decision_engine_caching():
    engine = DecisionEngine()
    ctx = RoutingContext(organization_id="org_test")
    p1 = engine.decide("gpt-4", ctx)
    stats = engine.cache.get_stats()
    assert stats["misses"] >= 1

    p2 = engine.decide("gpt-4", ctx)
    assert p1 == p2
    stats2 = engine.cache.get_stats()
    assert stats2["hits"] >= 1


@pytest.mark.asyncio
async def test_decision_engine_strategy_adapter():
    strategy = DecisionEngineRoutingStrategy()
    provider = await strategy.determine_provider_name(model=None, request=None)
    assert provider is not None
