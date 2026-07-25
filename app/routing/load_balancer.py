from app.core.exceptions import ProviderUnavailableException
from app.routing.load_balancing_policy import LoadBalancingPolicy
from app.routing.provider_pool import ProviderInstance, ProviderPool


class LoadBalancer:
    """Selects the best healthy provider instance using a load balancing policy."""

    def __init__(self, pool: ProviderPool, policy: LoadBalancingPolicy) -> None:
        self._pool = pool
        self._policy = policy

    def get_instance(self, provider_id: str) -> ProviderInstance:
        """Get the next healthy instance for the given provider."""
        healthy_instances = self._pool.get_healthy_instances(provider_id)
        
        if not healthy_instances:
            # Fallback: check if ANY instances exist, even if unhealthy, just to give a better error
            all_instances = self._pool.get_instances(provider_id)
            if not all_instances:
                raise ProviderUnavailableException(f"No instances registered for provider '{provider_id}'.")
            raise ProviderUnavailableException(f"All instances for provider '{provider_id}' are currently unhealthy.")

        return self._policy.select_instance(healthy_instances)
