import asyncio

from app.core.logger import get_logger
from app.routing.failover_policy import FailoverPolicy
from app.routing.provider_pool import ProviderInstance
from app.services.batching.batch_entry import Batch
from app.services.metrics_service import MetricsService

logger = get_logger("app.batching.executor")

class BatchExecutor:
    """Executes a batch of requests, delegating to the appropriate provider via load balancer."""

    def __init__(self, failover_policy: FailoverPolicy, metrics: MetricsService) -> None:
        self._failover_policy = failover_policy
        self._metrics = metrics

    async def execute_batch(self, batch: Batch) -> None:
        """Execute a formed batch of requests using failover policy."""
        if batch.size() == 0:
            return

        logger.info(f"Executing batch of size {batch.size()} for provider {batch.key.provider_id}")

        async def execute_on_instance(instance: ProviderInstance) -> None:
            provider = instance.provider
            
            for entry in batch.entries:
                if entry.cancellation_state.is_set():
                    continue

                if entry.is_streaming:
                    try:
                        async for chunk in provider.stream(request=entry.request):
                            if entry.cancellation_state.is_set():
                                break
                            await entry.stream_queue.put(chunk)
                        await entry.stream_queue.put(None)  # Sentinel
                    except Exception as exc:
                        await entry.stream_queue.put(exc)
                else:
                    response = await provider.generate(request=entry.request)
                    if not entry.result_future.done():
                        entry.result_future.set_result(response)

        try:
            await self._failover_policy.execute_with_failover(
                provider_id=batch.key.provider_id,
                execute_fn=execute_on_instance
            )
        except Exception as exc:
            logger.error(f"Failed to execute batch completely: {exc}")
            # Fail all entries in the batch that are still pending
            for entry in batch.entries:
                if entry.cancellation_state.is_set():
                    continue
                if entry.is_streaming:
                    asyncio.create_task(entry.stream_queue.put(exc))
                elif not entry.result_future.done():
                    entry.result_future.set_exception(exc)
