import threading
from typing import Any, Callable, Dict, List, Optional

from .routing_context import RoutingContext


class RoutingRule:
    """Individual rule for deterministic routing decisions."""

    def __init__(
        self,
        name: str,
        priority: int,
        condition: Callable[[RoutingContext], bool],
        target_policy: Optional[str] = None,
        target_provider: Optional[str] = None,
        excluded_providers: Optional[List[str]] = None,
        description: str = "",
    ):
        self.name = name
        self.priority = priority
        self.condition = condition
        self.target_policy = target_policy
        self.target_provider = target_provider
        self.excluded_providers = excluded_providers or []
        self.description = description

    def matches(self, context: RoutingContext) -> bool:
        try:
            return self.condition(context)
        except Exception:
            return False


class RuleEngine:
    """Rule engine that evaluates priority-ordered rules against RoutingContext."""

    def __init__(self):
        self._lock = threading.RLock()
        self._rules: List[RoutingRule] = []
        self._init_default_rules()

    def _init_default_rules(self):
        # Rule: Enterprise tier requests route to latency_optimized policy
        enterprise_rule = RoutingRule(
            name="enterprise_tier",
            priority=100,
            condition=lambda ctx: ctx.request_metadata.get("tier") == "enterprise"
            or ctx.request_metadata.get("org_tier") == "enterprise",
            target_policy="latency_optimized",
            description="Route enterprise tier requests to latency optimized policy",
        )
        # Rule: Low cost requirement routes to cost_optimized policy
        cost_sensitive_rule = RoutingRule(
            name="cost_sensitive",
            priority=50,
            condition=lambda ctx: ctx.request_metadata.get("cost_sensitive") is True,
            target_policy="cost_optimized",
            description="Route cost sensitive requests to cost optimized policy",
        )
        self.add_rule(enterprise_rule)
        self.add_rule(cost_sensitive_rule)

    def add_rule(self, rule: RoutingRule) -> None:
        with self._lock:
            self._rules.append(rule)
            self._rules.sort(key=lambda r: r.priority, reverse=True)

    def remove_rule(self, name: str) -> bool:
        with self._lock:
            initial_len = len(self._rules)
            self._rules = [r for r in self._rules if r.name != name]
            return len(self._rules) < initial_len

    def evaluate(self, context: RoutingContext) -> Optional[Dict[str, Any]]:
        """Evaluate rules in priority order and return matching rule directives."""
        with self._lock:
            for rule in self._rules:
                if rule.matches(context):
                    directives = {
                        "matched_rule": rule.name,
                        "target_policy": rule.target_policy,
                        "target_provider": rule.target_provider,
                        "excluded_providers": rule.excluded_providers,
                    }
                    if context:
                        context.record_trace("rule_matched", directives)
                    return directives
        return None

    def filter_excluded_providers(
        self, providers: List[str], context: RoutingContext
    ) -> List[str]:
        """Apply rule exclusions and context-driven restrictions (e.g. region, max_cost)."""
        excluded = set(context.request_metadata.get("excluded_providers", []))
        restricted_region = context.request_metadata.get("region")

        result = []
        for p in providers:
            if p in excluded:
                continue
            if restricted_region and context.request_metadata.get(f"{p}_region") not in (
                None,
                restricted_region,
            ):
                continue
            result.append(p)
        return result
