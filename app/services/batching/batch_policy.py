from app.services.batching.batch_config import BatchConfig
from app.services.batching.batch_entry import Batch, BatchKey
from app.services.request_scheduler import QueueEntry


class BatchPolicy:
    """Abstraction for determining batchability and dispatch conditions."""

    def __init__(self, config: BatchConfig) -> None:
        self._config = config

    def is_batchable(self, entry: QueueEntry) -> bool:
        """Decide if a queue entry can be batched."""
        if not self._config.enabled:
            return False

        # Phase 2.2: Batching non-streaming requests only is acceptable.
        if entry.is_streaming:
            return False

        return True

    def get_batch_key(self, entry: QueueEntry, provider_id: str) -> BatchKey:
        """Compute the structured BatchKey for an entry."""
        return BatchKey(
            provider_id=provider_id,
            model_id=entry.request.model,
            stream=entry.is_streaming,
        )

    def should_dispatch(self, batch: Batch) -> bool:
        """Determine if a batch meets the conditions for dispatch."""
        if batch.size() >= self._config.max_batch_size:
            return True

        if batch.elapsed_ms() >= self._config.max_batch_wait_ms:
            return True

        return False
