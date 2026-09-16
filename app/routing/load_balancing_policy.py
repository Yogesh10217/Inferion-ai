import random
from abc import ABC, abstractmethod
from enum import Enum
from typing import List

from app.routing.provider_pool import ProviderInstance


class LoadBalancingStrategy(str, Enum):
    ROUND_ROBIN = "round_robin"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    LEAST_CONNECTIONS = "least_connections"
    RANDOM = "random"


class LoadBalancingPolicy(ABC):
    """Base class for load balancing strategies."""

    @abstractmethod
    def select_instance(self, instances: List[ProviderInstance]) -> ProviderInstance:
        """Select a single instance from a list of healthy instances."""


class RoundRobinPolicy(LoadBalancingPolicy):
    def __init__(self) -> None:
        self._counters: dict[str, int] = {}

    def select_instance(self, instances: List[ProviderInstance]) -> ProviderInstance:
        if not instances:
            raise ValueError("No healthy instances available.")

        # We assume they all belong to the same provider_id, so we can track index by provider_id
        provider_id = instances[0].provider_id

        current_index = self._counters.get(provider_id, 0)
        selected = instances[current_index % len(instances)]
        self._counters[provider_id] = current_index + 1

        return selected


class WeightedRoundRobinPolicy(LoadBalancingPolicy):
    def __init__(self) -> None:
        self._counters: dict[str, int] = {}

    def select_instance(self, instances: List[ProviderInstance]) -> ProviderInstance:
        if not instances:
            raise ValueError("No healthy instances available.")

        provider_id = instances[0].provider_id

        # Flatten by weight: if instance A has weight 2, put it in list twice
        weighted_list = []
        for inst in instances:
            weighted_list.extend([inst] * max(1, inst.weight))

        current_index = self._counters.get(provider_id, 0)
        selected = weighted_list[current_index % len(weighted_list)]
        self._counters[provider_id] = current_index + 1

        return selected


class LeastConnectionsPolicy(LoadBalancingPolicy):
    def select_instance(self, instances: List[ProviderInstance]) -> ProviderInstance:
        if not instances:
            raise ValueError("No healthy instances available.")

        return min(instances, key=lambda inst: inst.health._active_requests)


class RandomPolicy(LoadBalancingPolicy):
    def select_instance(self, instances: List[ProviderInstance]) -> ProviderInstance:
        if not instances:
            raise ValueError("No healthy instances available.")

        return random.choice(instances)


def get_policy(strategy: LoadBalancingStrategy) -> LoadBalancingPolicy:
    """Factory for load balancing policies."""
    policies = {
        LoadBalancingStrategy.ROUND_ROBIN: RoundRobinPolicy,
        LoadBalancingStrategy.WEIGHTED_ROUND_ROBIN: WeightedRoundRobinPolicy,
        LoadBalancingStrategy.LEAST_CONNECTIONS: LeastConnectionsPolicy,
        LoadBalancingStrategy.RANDOM: RandomPolicy,
    }
    return policies[strategy]()
