import asyncio

from app.core.logger import get_logger
from app.routing.request_router import RequestRouter, RoutingRequest
from app.services.batching.batch_entry import Batch
from app.services.metrics_service import MetricsService

logger = get_logger("app.batching.executor")

class BatchExecutor:
    """Executes a batch of requests, delegating to the appropriate provider."""

    def __init__(self, router: RequestRouter, metrics: MetricsService) -> None:
        self._router = router
        self._metrics = metrics

    async def execute_batch(self, batch: Batch) -> None:
        """Execute a formed batch of requests.
        
        In Phase 2.2, this executes requests sequentially within the batch.
        Future phases will introduce provider-native batch execution.
        """
        if batch.size() == 0:
            return

        logger.info(f"Executing batch of size {batch.size()} for model {batch.key.model_id}")

        try:
            # Resolve the provider for this batch
            provider = await self._router.route(RoutingRequest(model_id=batch.key.model_id))
            
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
                    try:
                        response = await provider.generate(request=entry.request)
                        if not entry.result_future.done():
                            entry.result_future.set_result(response)
                    except Exception as exc:
                        if not entry.result_future.done():
                            entry.result_future.set_exception(exc)
        except Exception as exc:
            logger.error(f"Failed to execute batch: {exc}")
            # Fail all entries in the batch
            for entry in batch.entries:
                if entry.cancellation_state.is_set():
                    continue
                if entry.is_streaming:
                    asyncio.create_task(entry.stream_queue.put(exc))
                elif not entry.result_future.done():
                    entry.result_future.set_exception(exc)
