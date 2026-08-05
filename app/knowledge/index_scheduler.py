import asyncio
import logging
from typing import Callable, Awaitable
from app.knowledge.pipeline import DocumentContext

logger = logging.getLogger(__name__)

class IndexScheduler:
    """Background scheduling system for document indexing."""
    
    def __init__(self, pipeline_runner_func: Callable[[DocumentContext], Awaitable[DocumentContext]]):
        self.queue: asyncio.Queue[DocumentContext] = asyncio.Queue()
        self.pipeline_runner_func = pipeline_runner_func
        self._worker_task = None

    async def start(self):
        """Starts the background worker."""
        if self._worker_task is None:
            self._worker_task = asyncio.create_task(self._worker())
            logger.info("IndexScheduler background worker started.")

    async def stop(self):
        """Stops the background worker."""
        if self._worker_task:
            self._worker_task.cancel()
            try:
                await self._worker_task
            except asyncio.CancelledError:
                pass
            self._worker_task = None
            logger.info("IndexScheduler background worker stopped.")

    async def schedule(self, context: DocumentContext):
        """Schedules a document for indexing."""
        await self.queue.put(context)
        logger.info(f"Document {context.document_id} scheduled for indexing.")

    async def _worker(self):
        """Background worker that processes the queue."""
        while True:
            context = await self.queue.get()
            try:
                await self.pipeline_runner_func(context)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error processing document {context.document_id} in background: {e}")
            finally:
                self.queue.task_done()
