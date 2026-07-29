import pytest
from app.routing.routing_policy import RoutingPolicy
from app.routing.policy_registry import PolicyRegistry


def test_routing_policy_normalization():
    policy = RoutingPolicy("custom", weights={"health": 2.0, "latency": 2.0})
    assert policy.weights["health"] == 0.5
    assert policy.weights["latency"] == 0.5


def test_policy_registry_org_overrides():
    registry = PolicyRegistry()
    org_policy = RoutingPolicy("org_special", organization_id="org_123", priority=20)
    registry.add_policy(org_policy)

    fetched = registry.get_policy_for_organization("org_123")
    assert fetched.name == "org_special"

    fallback = registry.get_policy_for_organization("org_unknown")
    assert fallback.name == "default"
