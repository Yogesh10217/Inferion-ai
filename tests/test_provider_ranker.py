from app.routing.provider_ranker import ProviderRanker
from app.routing.routing_metrics import RoutingMetrics
from app.routing.routing_policy import RoutingPolicy


def test_provider_ranker_scoring():
    ranker = ProviderRanker()
    policy = RoutingPolicy(name="test", weights={"latency": 0.8, "health": 0.2})
    metrics = RoutingMetrics()
    metrics.record_success("p1", 50.0)
    metrics.record_success("p2", 500.0)

    health = {"p1": True, "p2": True}
    ranked = ranker.rank(["p1", "p2"], policy, metrics, health)
    assert len(ranked) == 2
    # p1 with 50ms latency should rank higher than p2 with 500ms latency
    assert ranked[0][0] == "p1"
    assert ranked[0][1] > ranked[1][1]
