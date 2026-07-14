from __future__ import annotations

from typing import AsyncIterator

from app.providers.base_provider import BaseProvider
from app.schemas.inference_response import InferenceResponse
from app.schemas.request import InferenceRequest


class StreamingManager:
    """Intermediary between InferenceService and providers to manage streaming logic."""

    async def stream(self, provider: BaseProvider, request: InferenceRequest) -> AsyncIterator[InferenceResponse]:
        """Delegate streaming to the provider and yield normalized InferenceResponse chunks."""
        async for chunk in provider.stream(request=request):
            yield chunk
