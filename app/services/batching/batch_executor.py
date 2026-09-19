import asyncio
from typing import Optional

from app.cache.cache_manager import CacheManager
from app.core.logger import get_logger
from app.resilience.bulkhead import BulkheadRegistry
from app.resilience.circuit_breaker import CircuitBreakerOpenException, CircuitBreakerRegistry
from app.routing.failover_policy import FailoverPolicy
from app.routing.provider_pool import ProviderInstance
from app.services.batching.batch_entry import Batch
from app.services.dead_letter_queue import DeadLetterQueue, DLQEntry
from app.services.metrics_service import MetricsService

logger = get_logger("app.batching.executor")


class BatchExecutor:
    """Executes a batch of requests, delegating to the appropriate provider via load balancer with circuit breaker, bulkhead, and DLQ protection."""

    def __init__(
        self,
        failover_policy: FailoverPolicy,
        metrics: MetricsService,
        cache_manager: Optional[CacheManager] = None,
        circuit_breaker_registry: Optional[CircuitBreakerRegistry] = None,
        bulkhead_registry: Optional[BulkheadRegistry] = None,
        dead_letter_queue: Optional[DeadLetterQueue] = None,
    ) -> None:
        self._failover_policy = failover_policy
        self._metrics = metrics
        self._cache_manager = cache_manager
        self._circuit_breaker_registry = circuit_breaker_registry
        self._bulkhead_registry = bulkhead_registry
        self._dead_letter_queue = dead_letter_queue

    async def execute_batch(self, batch: Batch) -> None:
        """Execute a formed batch of requests using failover policy, circuit breaker, bulkhead and DLQ fallback."""
        if batch.size() == 0:
            return

        # Pre-execution Cache Lookup
        if self._cache_manager:
            for entry in batch.entries:
                if entry.cancellation_state.is_set():
                    continue
                cached_response = await self._cache_manager.lookup(entry)
                if cached_response is not None:
                    if not entry.result_future.done():
                        entry.result_future.set_result(cached_response)

        # Filter entries that still need execution (not cached and not cancelled)
        pending_entries = [
            entry for entry in batch.entries if not entry.result_future.done() and not entry.cancellation_state.is_set()
        ]

        if not pending_entries:
            return

        logger.info(
            f"Executing batch of size {len(pending_entries)} (original size {batch.size()}) for provider {batch.key.provider_id}"
        )

        async def execute_on_instance(instance: ProviderInstance) -> None:
            provider = instance.provider
            provider_id = instance.provider_id

            # Check Circuit Breaker
            if self._circuit_breaker_registry:
                breaker = self._circuit_breaker_registry.get_breaker(provider_id)
                if not breaker.allow_request():
                    rec_sec = max(
                        0.0,
                        breaker.policy.recovery_timeout_seconds
                        - (asyncio.get_event_loop().time() - breaker.last_failure_time),
                    )
                    raise CircuitBreakerOpenException(provider_id, rec_sec)

            bulkhead = self._bulkhead_registry.get_bulkhead(provider_id) if self._bulkhead_registry else None

            async def _run_entry(entry):
                if entry.cancellation_state.is_set():
                    return
                if entry.is_streaming:
                    try:
                        async for chunk in provider.stream(request=entry.request):
                            if entry.cancellation_state.is_set():
                                break
                            await entry.stream_queue.put(chunk)
                        await entry.stream_queue.put(None)  # Sentinel
                        if self._circuit_breaker_registry:
                            self._circuit_breaker_registry.get_breaker(provider_id).record_success()
                    except Exception as exc:
                        if self._circuit_breaker_registry:
                            self._circuit_breaker_registry.get_breaker(provider_id).record_failure(exc)
                        await entry.stream_queue.put(exc)
                        raise
                else:
                    try:
                        response = await provider.generate(request=entry.request)
                        if not entry.result_future.done():
                            entry.result_future.set_result(response)

                        if self._cache_manager:
                            await self._cache_manager.store(entry, response)

                        if self._circuit_breaker_registry:
                            self._circuit_breaker_registry.get_breaker(provider_id).record_success()
                    except Exception as exc:
                        if self._circuit_breaker_registry:
                            self._circuit_breaker_registry.get_breaker(provider_id).record_failure(exc)
                        raise

            for entry in pending_entries:
                if entry.cancellation_state.is_set():
                    continue
                if bulkhead:
                    await bulkhead.execute_async(_run_entry, entry)
                else:
                    await _run_entry(entry)

        try:
            await self._failover_policy.execute_with_failover(
                provider_id=batch.key.provider_id, execute_fn=execute_on_instance
            )
        except Exception as exc:
            logger.error(f"Failed to execute batch completely: {exc}")
            for entry in pending_entries:
                if entry.cancellation_state.is_set():
                    continue

                if self._dead_letter_queue:
                    await self._dead_letter_queue.put(
                        DLQEntry(
                            model=entry.request.model,
                            provider_id=batch.key.provider_id,
                            error=str(exc),
                        )
                    )

                if entry.is_streaming:
                    asyncio.create_task(entry.stream_queue.put(exc))
                elif not entry.result_future.done():
                    entry.result_future.set_exception(exc)
