import asyncio
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, AsyncIterator, Dict, Optional

from app.core.logger import get_logger
from app.routing.request_router import RequestRouter, RoutingRequest
from app.schemas.inference_response import InferenceResponse
from app.schemas.request import InferenceRequest
from app.services.metrics_service import MetricsService

logger = get_logger("app.scheduler")

class SchedulingPolicy(str, Enum):
    FIFO = "fifo"
    PRIORITY = "priority"
    FAIR = "fair"

@dataclass
class SchedulerConfig:
    max_queue_size: int = 1000
    policy: SchedulingPolicy = SchedulingPolicy.FIFO

@dataclass
class QueueEntry:
    request: InferenceRequest
    is_streaming: bool
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    enqueue_time: float = field(default_factory=time.time)
    priority: int = 0
    cancellation_state: asyncio.Event = field(default_factory=asyncio.Event)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Futures to return the result back to the caller
    result_future: asyncio.Future = field(default_factory=asyncio.Future)
    stream_queue: asyncio.Queue = field(default_factory=asyncio.Queue)

class RequestQueue:
    """Internal async queue wrapping asyncio.Queue."""
    
    def __init__(self, max_size: int = 0):
        self._queue: asyncio.Queue[QueueEntry] = asyncio.Queue(maxsize=max_size)
        
    async def enqueue(self, entry: QueueEntry) -> None:
        await self._queue.put(entry)
        
    async def dequeue(self) -> QueueEntry:
        return await self._queue.get()
        
    def queue_size(self) -> int:
        return self._queue.qsize()
        
    def pending_requests(self) -> int:
        return self.queue_size()
        
    def shutdown(self) -> None:
        """Cancel all pending requests in the queue."""
        while not self._queue.empty():
            try:
                entry = self._queue.get_nowait()
                entry.cancellation_state.set()
                if not entry.result_future.done():
                    entry.result_future.cancel()
                self._queue.task_done()
            except asyncio.QueueEmpty:
                break

class RequestScheduler:
    """Scheduler for enqueueing and dispatching inference requests."""
    
    def __init__(
        self,
        router: RequestRouter,
        metrics: MetricsService,
        config: Optional[SchedulerConfig] = None,
    ) -> None:
        self._router = router
        self._metrics = metrics
        self._config = config or SchedulerConfig()
        self._queue = RequestQueue(max_size=self._config.max_queue_size)
        self._worker_task: Optional[asyncio.Task] = None
        self._is_running = False

    def start(self) -> None:
        """Start the background worker."""
        current_loop = asyncio.get_running_loop()
        
        needs_restart = False
        if not self._is_running or self._worker_task is None or self._worker_task.done():
            needs_restart = True
        elif hasattr(self._worker_task, "get_loop") and self._worker_task.get_loop() != current_loop:
            # Handle TestClient creating new event loops per test
            self._worker_task.cancel()
            needs_restart = True
            
        if needs_restart:
            self._is_running = True
            self._worker_task = current_loop.create_task(self._worker_loop())

    async def shutdown(self) -> None:
        """Stop the background worker and cancel pending requests."""
        self._is_running = False
        if self._worker_task:
            self._worker_task.cancel()
            try:
                await self._worker_task
            except asyncio.CancelledError:
                pass
        self._queue.shutdown()

    async def generate(self, request: InferenceRequest) -> InferenceResponse:
        """Enqueue a request and wait for the response."""
        entry = QueueEntry(request=request, is_streaming=False)
        self._metrics.record_enqueue()
        await self._queue.enqueue(entry)
        
        # Start worker if not already running (lazy start)
        self.start()
        
        try:
            return await entry.result_future
        except asyncio.CancelledError:
            entry.cancellation_state.set()
            raise

    async def stream(self, request: InferenceRequest) -> AsyncIterator[InferenceResponse]:
        """Enqueue a streaming request and yield its response chunks."""
        entry = QueueEntry(request=request, is_streaming=True)
        self._metrics.record_enqueue()
        await self._queue.enqueue(entry)
        
        # Start worker if not already running (lazy start)
        self.start()
        
        try:
            while True:
                chunk = await entry.stream_queue.get()
                if chunk is None:  # Sentinel value for end of stream
                    break
                if isinstance(chunk, Exception):
                    raise chunk
                yield chunk
        except asyncio.CancelledError:
            entry.cancellation_state.set()
            raise

    async def _worker_loop(self) -> None:
        """Background loop to process requests."""
        while self._is_running:
            try:
                entry = await self._queue.dequeue()
            except asyncio.CancelledError:
                break
                
            wait_time_ms = (time.time() - entry.enqueue_time) * 1000
            self._metrics.record_dequeue(wait_time_ms)
            
            if entry.cancellation_state.is_set():
                continue
                
            # Dispatch the request without awaiting it here so we don't block the queue
            # In a full batching system, this would gather multiple entries.
            asyncio.create_task(self._process_entry(entry))

    async def _process_entry(self, entry: QueueEntry) -> None:
        """Process a single queue entry by resolving the provider and executing."""
        try:
            if entry.cancellation_state.is_set():
                return
                
            provider = await self._router.route(RoutingRequest(model_id=entry.request.model))
            
            if entry.is_streaming:
                try:
                    async for chunk in provider.stream(request=entry.request):
                        if entry.cancellation_state.is_set():
                            break
                        await entry.stream_queue.put(chunk)
                    await entry.stream_queue.put(None)  # End of stream sentinel
                except Exception as exc:
                    await entry.stream_queue.put(exc)
            else:
                response = await provider.generate(request=entry.request)
                if not entry.result_future.done():
                    entry.result_future.set_result(response)
                    
        except Exception as exc:
            if entry.is_streaming:
                await entry.stream_queue.put(exc)
            elif not entry.result_future.done():
                entry.result_future.set_exception(exc)
