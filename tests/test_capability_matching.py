from app.routing.capability_registry import CapabilityRegistry


def test_capability_registry():
    registry = CapabilityRegistry()
    registry.register("p_vision", ["chat", "vision"])
    registry.register("p_text", ["chat"])

    assert registry.has_capability("p_vision", "vision")
    assert not registry.has_capability("p_text", "vision")

    filtered = registry.filter_providers_by_capabilities(["p_vision", "p_text"], ["vision"])
    assert filtered == ["p_vision"]

    providers_with_vision = registry.get_providers_with_capability("vision")
    assert providers_with_vision == ["p_vision"]
