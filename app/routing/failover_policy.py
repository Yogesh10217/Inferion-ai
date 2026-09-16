import asyncio
from typing import Any, Awaitable, Callable

from app.core.exceptions import ProviderUnavailableException
from app.core.logger import get_logger
from app.routing.load_balancer import LoadBalancer
from app.routing.provider_pool import ProviderInstance

logger = get_logger("app.routing.failover")


class FailoverPolicy:
    """Handles retry and failover logic for provider execution."""

    def __init__(self, load_balancer: LoadBalancer, max_retries: int = 2) -> None:
        self._load_balancer = load_balancer
        self.max_retries = max_retries

    async def execute_with_failover(
        self,
        provider_id: str,
        execute_fn: Callable[[ProviderInstance], Awaitable[Any]],
    ) -> Any:
        """
        Execute a function on a healthy provider instance, with automatic failover.
        The execute_fn should raise an exception if it encounters a provider-level error.
        """
        last_exception = None

        for attempt in range(self.max_retries + 1):
            try:
                instance = self._load_balancer.get_instance(provider_id)
            except ProviderUnavailableException as exc:
                if attempt == 0:
                    raise  # No instances available at all
                # If we've exhausted all instances on retries, raise the last execution exception or this one
                raise ProviderUnavailableException(f"Failover exhausted. {exc}") from last_exception

            await instance.health.record_active()
            start_time = asyncio.get_running_loop().time()

            try:
                result = await execute_fn(instance)

                # Execution successful
                latency_ms = (asyncio.get_running_loop().time() - start_time) * 1000
                await instance.health.record_success(latency_ms)
                return result

            except Exception as exc:
                last_exception = exc
                logger.warning(f"Execution failed on instance {instance.instance_id} (attempt {attempt + 1}/{self.max_retries + 1}): {exc}")
                await instance.health.record_failure()

                # Check if it's a fatal error that shouldn't be retried (e.g. invalid request format)
                # For now, we assume all exceptions during execution are network/provider related for failover,
                # but in a real system we'd check if exc is retryable (like 503 vs 400).
                # To be simple for Phase 2.3, we'll retry all exceptions.

                if attempt == self.max_retries:
                    raise exc

        # Should never reach here due to raise in loop
        raise ProviderUnavailableException("Failover failed") from last_exception
