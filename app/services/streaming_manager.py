from __future__ import annotations

from typing import AsyncIterator, Optional

from app.schemas.inference_response import InferenceResponse
from app.schemas.request import InferenceRequest
from app.services.request_scheduler import RequestScheduler


class StreamingManager:
    """Intermediary between InferenceService and the scheduling layer for stream management."""

    def __init__(self, scheduler: Optional[RequestScheduler] = None) -> None:
        self._scheduler = scheduler

    async def stream(self, request: InferenceRequest) -> AsyncIterator[InferenceResponse]:
        """Delegate streaming to the scheduler and yield normalized InferenceResponse chunks."""
        if self._scheduler is None:
            raise RuntimeError("RequestScheduler not configured")

        async for chunk in self._scheduler.stream(request=request):
            yield chunk
