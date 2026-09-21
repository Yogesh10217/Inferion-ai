from app.routing.provider_selector import ProviderSelector


def test_provider_selector_failover():
    selector = ProviderSelector(fallback_provider="mock_fallback")
    ranked = [("p1", 0.9), ("p2", 0.8), ("p3", 0.7)]

    # Normal top selection
    selected = selector.select(ranked)
    assert selected == "p1"

    # Selection with unhealthy p1 and failed p2
    selected_failover = selector.select(ranked, unhealthy_providers={"p1"}, failed_attempts=["p2"])
    assert selected_failover == "p3"

    # Full fallback when all failed
    selected_fallback = selector.select(ranked, failed_attempts=["p1", "p2", "p3"])
    assert selected_fallback == "mock_fallback"
