import asyncio
from typing import Dict, Optional

from app.core.logger import get_logger
from app.services.batching.batch_entry import Batch, BatchKey
from app.services.batching.batch_executor import BatchExecutor
from app.services.batching.batch_policy import BatchPolicy
from app.services.metrics_service import MetricsService
from app.services.request_scheduler import QueueEntry

logger = get_logger("app.batching.collector")


class BatchCollector:
    """Collects and groups inference requests into batches."""

    def __init__(
        self,
        policy: BatchPolicy,
        executor: BatchExecutor,
        metrics: MetricsService,
    ) -> None:
        self._policy = policy
        self._executor = executor
        self._metrics = metrics
        self._buckets: Dict[BatchKey, Batch] = {}
        self._lock = asyncio.Lock()

        self._is_running = False
        self._flush_task: Optional[asyncio.Task] = None

    def start(self) -> None:
        """Start the background task that checks for batch timeouts."""
        if not self._is_running:
            self._is_running = True
            current_loop = asyncio.get_running_loop()
            self._flush_task = current_loop.create_task(self._flush_loop())

    async def shutdown(self) -> None:
        """Stop the background task and flush remaining batches."""
        self._is_running = False
        if self._flush_task:
            self._flush_task.cancel()
            try:
                await self._flush_task
            except asyncio.CancelledError:
                pass

        # Flush any remaining batches immediately
        async with self._lock:
            for key, batch in self._buckets.items():
                if batch.size() > 0:
                    self._dispatch(batch)
            self._buckets.clear()

    async def add_entry(self, entry: QueueEntry) -> None:
        """Add an entry to the appropriate batch or dispatch immediately."""
        # Ensure flush loop is running (lazy start for TestClient resilience)
        if not self._is_running or (self._flush_task and self._flush_task.done()):
            self.start()

        # If not batchable, dispatch as a single-item batch immediately
        if not self._policy.is_batchable(entry):
            try:
                key = self._policy.get_batch_key(entry, entry.decision.provider_id)
            except Exception as exc:
                self._fail_entry(entry, exc)
                return

            batch = Batch(key=key)
            batch.add_entry(entry)
            self._metrics.record_single_request_fallback()
            self._dispatch(batch)
            return

        # Use the routing decision already attached to the entry
        try:
            key = self._policy.get_batch_key(entry, entry.decision.provider_id)
        except Exception as exc:
            self._fail_entry(entry, exc)
            return

        async with self._lock:
            batch = self._buckets.get(key)
            if batch is None:
                batch = Batch(key=key)
                self._buckets[key] = batch
                self._metrics.record_active_batch_added()

            batch.add_entry(entry)

            if self._policy.should_dispatch(batch):
                self._buckets.pop(key, None)
                self._metrics.record_active_batch_removed()
                self._dispatch(batch)

    def _fail_entry(self, entry: QueueEntry, exc: Exception) -> None:
        if entry.is_streaming:
            asyncio.create_task(entry.stream_queue.put(exc))
        elif not entry.result_future.done():
            entry.result_future.set_exception(exc)

    def _dispatch(self, batch: Batch) -> None:
        """Send the batch to the executor in a background task."""
        # Dispatch delay metric
        self._metrics.record_batch_dispatch(batch.size(), batch.elapsed_ms())
        asyncio.create_task(self._executor.execute_batch(batch))

    async def _flush_loop(self) -> None:
        """Periodically check all buckets for timeouts."""
        check_interval = max(0.01, self._policy._config.max_batch_wait_ms / 2000.0)  # Check roughly twice per timeout window

        while self._is_running:
            try:
                await asyncio.sleep(check_interval)

                async with self._lock:
                    dispatched_keys = []
                    for key, batch in self._buckets.items():
                        if self._policy.should_dispatch(batch):
                            dispatched_keys.append(key)
                            self._dispatch(batch)

                    for key in dispatched_keys:
                        self._buckets.pop(key, None)
                        self._metrics.record_active_batch_removed()
            except asyncio.CancelledError:
                break
            except Exception as exc:
                logger.error(f"Error in BatchCollector flush loop: {exc}")
