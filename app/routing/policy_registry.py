import threading
from typing import Dict, List, Optional

from .routing_policy import RoutingPolicy


class PolicyRegistry:
    """Central registry for managing routing policies with organization overrides."""

    def __init__(self):
        self._lock = threading.RLock()
        self._policies: Dict[str, RoutingPolicy] = {}
        self._org_policies: Dict[str, str] = {}  # org_id -> policy_name
        self._default_policy_name: Optional[str] = None
        self._init_defaults()

    def _init_defaults(self):
        default_policy = RoutingPolicy(
            name="default",
            description="Default balanced routing policy",
            is_default=True,
            priority=0,
        )
        latency_policy = RoutingPolicy(
            name="latency_optimized",
            weights={
                "health": 0.3,
                "latency": 0.5,
                "cost": 0.05,
                "success_rate": 0.1,
                "capability_match": 0.05,
                "org_policy": 0.0,
            },
            description="Optimized for low latency",
            priority=5,
        )
        cost_policy = RoutingPolicy(
            name="cost_optimized",
            weights={
                "health": 0.3,
                "latency": 0.1,
                "cost": 0.5,
                "success_rate": 0.05,
                "capability_match": 0.05,
                "org_policy": 0.0,
            },
            description="Optimized for lowest cost",
            priority=5,
        )
        self.add_policy(default_policy)
        self.add_policy(latency_policy)
        self.add_policy(cost_policy)

    def add_policy(self, policy: RoutingPolicy) -> None:
        """Register or update a routing policy."""
        with self._lock:
            self._policies[policy.name] = policy
            if policy.is_default or self._default_policy_name is None:
                self._default_policy_name = policy.name
            if policy.organization_id:
                self._org_policies[policy.organization_id] = policy.name

    def remove_policy(self, name: str) -> bool:
        """Remove a routing policy by name."""
        with self._lock:
            if name not in self._policies:
                return False
            del self._policies[name]
            if self._default_policy_name == name:
                self._default_policy_name = next(iter(self._policies.keys()), None)
            return True

    def get_policy(self, name: str) -> Optional[RoutingPolicy]:
        """Look up a policy by name."""
        with self._lock:
            return self._policies.get(name)

    def get_policy_for_organization(self, organization_id: Optional[str] = None) -> RoutingPolicy:
        """Retrieve policy for organization or return default policy."""
        with self._lock:
            if organization_id and organization_id in self._org_policies:
                policy_name = self._org_policies[organization_id]
                policy = self._policies.get(policy_name)
                if policy:
                    return policy

            default_name = self._default_policy_name or "default"
            return self._policies.get(default_name) or RoutingPolicy(name="fallback")

    def list_policies(self) -> List[RoutingPolicy]:
        """Return all registered policies sorted by priority descending."""
        with self._lock:
            return sorted(self._policies.values(), key=lambda p: p.priority, reverse=True)
