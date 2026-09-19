from typing import Dict, List, Optional, Tuple

from .routing_metrics import RoutingMetrics
from .routing_policy import RoutingPolicy


class ProviderRanker:
    """Calculates weighted scores for providers based on metrics, health, and policy weights."""

    def __init__(self, default_max_latency_ms: float = 2000.0, default_max_cost: float = 0.05):
        self.default_max_latency_ms = default_max_latency_ms
        self.default_max_cost = default_max_cost

    def rank(
        self,
        providers: List[str],
        policy: RoutingPolicy,
        metrics: RoutingMetrics,
        health_status: Dict[str, bool],
        capability_scores: Optional[Dict[str, float]] = None,
        org_preferences: Optional[Dict[str, float]] = None,
    ) -> List[Tuple[str, float]]:
        """Rank providers returning sorted list of (provider_id, normalized_score) descending."""
        if not providers:
            return []

        scored_providers: List[Tuple[str, float]] = []
        cap_scores = capability_scores or {}
        org_prefs = org_preferences or {}

        for provider_id in providers:
            # 1. Health component (1.0 if healthy, 0.0 if unhealthy)
            is_healthy = health_status.get(provider_id, True)
            health_score = 1.0 if is_healthy else 0.0

            # 2. Get provider metrics
            stats = metrics.get_provider_stats(provider_id)
            avg_latency = stats.get("avg_latency_ms", 100.0)
            success_rate = stats.get("success_rate", 1.0)
            cost = stats.get("estimated_cost_per_1k", 0.002)

            # 3. Normalize latency score (0 ms -> 1.0, max_latency -> 0.0)
            latency_score = max(0.0, 1.0 - (avg_latency / self.default_max_latency_ms))

            # 4. Normalize cost score (0 cost -> 1.0, max_cost -> 0.0)
            cost_score = max(0.0, 1.0 - (cost / self.default_max_cost))

            # 5. Success rate score
            success_score = max(0.0, min(1.0, success_rate))

            # 6. Capability & Org policy scores
            cap_score = cap_scores.get(provider_id, 1.0)
            org_score = org_prefs.get(provider_id, 0.5)

            # Calculate composite weighted score
            component_metrics = {
                "health": health_score,
                "latency": latency_score,
                "cost": cost_score,
                "success_rate": success_score,
                "capability_match": cap_score,
                "org_policy": org_score,
            }

            final_score = policy.calculate_score(component_metrics)
            scored_providers.append((provider_id, round(final_score, 4)))

        # Sort descending by score
        scored_providers.sort(key=lambda x: x[1], reverse=True)
        return scored_providers
