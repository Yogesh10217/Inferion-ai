from typing import List, Optional, Set, Tuple


class ProviderSelector:
    """Selects the optimal provider with failover, fallback, and circuit breaker filtering."""

    def __init__(self, fallback_provider: str = "mock_provider"):
        self.fallback_provider = fallback_provider

    def select(
        self,
        ranked_providers: List[Tuple[str, float]],
        unhealthy_providers: Optional[Set[str]] = None,
        tripped_circuit_breakers: Optional[Set[str]] = None,
        failed_attempts: Optional[List[str]] = None,
    ) -> Optional[str]:
        """Select the highest-ranked healthy, non-tripped, non-failed provider."""
        unhealthy = unhealthy_providers or set()
        circuits = tripped_circuit_breakers or set()
        failed = set(failed_attempts or [])

        for provider_id, score in ranked_providers:
            if provider_id in unhealthy:
                continue
            if provider_id in circuits:
                continue
            if provider_id in failed:
                continue
            return provider_id

        # Fallback if all candidates fail/unhealthy
        for provider_id, score in ranked_providers:
            if provider_id not in failed:
                return provider_id

        return self.fallback_provider

    def get_failover_sequence(
        self,
        ranked_providers: List[Tuple[str, float]],
        unhealthy_providers: Optional[Set[str]] = None,
    ) -> List[str]:
        """Generate full failover sequence of providers in priority order."""
        unhealthy = unhealthy_providers or set()
        sequence = [p for p, _ in ranked_providers if p not in unhealthy]
        # Append remaining as last-resort failover targets
        for p, _ in ranked_providers:
            if p not in sequence:
                sequence.append(p)
        if self.fallback_provider not in sequence:
            sequence.append(self.fallback_provider)
        return sequence
