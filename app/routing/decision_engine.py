import logging
import time
from typing import Dict, List, Optional

from .capability_registry import CapabilityRegistry
from .policy_registry import PolicyRegistry
from .provider_ranker import ProviderRanker
from .provider_selector import ProviderSelector
from .routing_cache import RoutingCache
from .routing_context import RoutingContext
from .routing_metrics import RoutingMetrics
from .routing_rules import RuleEngine

logger = logging.getLogger(__name__)


class DecisionEngine:
    """Full 9-stage pipeline managing intelligent routing decisions."""

    def __init__(
        self,
        capability_registry: Optional[CapabilityRegistry] = None,
        policy_registry: Optional[PolicyRegistry] = None,
        rule_engine: Optional[RuleEngine] = None,
        ranker: Optional[ProviderRanker] = None,
        selector: Optional[ProviderSelector] = None,
        metrics: Optional[RoutingMetrics] = None,
        cache: Optional[RoutingCache] = None,
    ):
        self.capability_registry = capability_registry or CapabilityRegistry()
        self.policy_registry = policy_registry or PolicyRegistry()
        self.rule_engine = rule_engine or RuleEngine()
        self.ranker = ranker or ProviderRanker()
        self.selector = selector or ProviderSelector()
        self.metrics = metrics or RoutingMetrics()
        self.cache = cache or RoutingCache()

        # Seed initial capabilities if empty
        self._seed_default_capabilities()

    def _seed_default_capabilities(self):
        all_caps = list(CapabilityRegistry.STANDARD_CAPABILITIES)
        self.capability_registry.register("mock_provider", all_caps)
        self.capability_registry.register("openai_provider", all_caps)
        self.capability_registry.register("anthropic_provider", all_caps)

    def decide(
        self,
        model_id: str,
        context: Optional[RoutingContext] = None,
        available_providers: Optional[List[str]] = None,
    ) -> str:
        """Execute full routing pipeline to determine optimal provider."""
        start_time = time.time()
        ctx = context or RoutingContext()

        # Check decision cache first
        cache_key = f"{model_id}:{ctx.organization_id}:{ctx.required_capabilities}"
        cached_decision = self.cache.get_decision(cache_key)
        if cached_decision:
            self.metrics.observe_cache_hit()
            ctx.record_trace("cache_hit", {"selected_provider": cached_decision})
            return cached_decision
        self.metrics.observe_cache_miss()

        # Candidates pool
        candidates = available_providers if available_providers is not None else [
            "openai_provider",
            "anthropic_provider",
            "mock_provider",
        ]

        # Stage 1: Capability Filtering
        req_caps = ctx.required_capabilities or ctx.request_metadata.get("capabilities", [])
        stage1_candidates = self.capability_registry.filter_providers_by_capabilities(
            candidates, req_caps
        )
        if not stage1_candidates:
            stage1_candidates = list(candidates)
        ctx.record_trace("capability_filtering", {"remaining": stage1_candidates})

        # Stage 2: Rule Evaluation
        rule_directives = self.rule_engine.evaluate(ctx)
        target_policy_name = None
        if rule_directives:
            if rule_directives.get("target_provider") in stage1_candidates:
                ctx.record_trace("rule_override_provider", rule_directives)
                selected = rule_directives["target_provider"]
                self.cache.set_decision(cache_key, selected)
                self.metrics.observe_decision("rule_override", selected, time.time() - start_time)
                return selected
            target_policy_name = rule_directives.get("target_policy")
            stage1_candidates = self.rule_engine.filter_excluded_providers(
                stage1_candidates, ctx
            )
        ctx.record_trace("rule_evaluation", {"remaining": stage1_candidates})

        # Stage 3: Policy Evaluation
        if target_policy_name:
            policy = self.policy_registry.get_policy(target_policy_name)
        else:
            policy = self.policy_registry.get_policy_for_organization(ctx.organization_id)
        ctx.record_trace("policy_evaluation", {"applied_policy": policy.name})

        # Stage 4: Health Evaluation
        health_status: Dict[str, bool] = {}
        healthy_candidates: List[str] = []
        for p in stage1_candidates:
            h = self.cache.get_health(p)
            if h is None:
                h = True  # Default healthy
            health_status[p] = h
            if h:
                healthy_candidates.append(p)
        ctx.record_trace("health_evaluation", {"health_status": health_status})

        candidates_to_score = healthy_candidates if healthy_candidates else stage1_candidates

        # Stage 5 & 6: Weighted Scoring & Provider Ranking
        ranked_providers = self.ranker.rank(
            providers=candidates_to_score,
            policy=policy,
            metrics=self.metrics,
            health_status=health_status,
            org_preferences=ctx.request_metadata.get("org_preferences"),
        )
        ctx.record_trace("provider_ranking", {"ranked": ranked_providers})

        # Stage 7 & 8: Provider Selection & Failover
        unhealthy_set = {p for p, h in health_status.items() if not h}
        failed_attempts = ctx.request_metadata.get("failed_attempts", [])
        selected_provider = self.selector.select(
            ranked_providers=ranked_providers,
            unhealthy_providers=unhealthy_set,
            failed_attempts=failed_attempts,
        )

        # Stage 9: Final Decision
        final_provider = selected_provider or (candidates[0] if candidates else "mock_provider")
        duration = time.time() - start_time

        self.cache.set_decision(cache_key, final_provider)
        self.metrics.observe_decision(policy.name, final_provider, duration)
        ctx.record_trace("final_decision", {"selected_provider": final_provider, "duration_sec": round(duration, 5)})

        return final_provider
