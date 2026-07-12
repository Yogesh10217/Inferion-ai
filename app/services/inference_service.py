from __future__ import annotations

import json
import time
from abc import ABC, abstractmethod
from typing import Any, AsyncIterator

from app.core.exceptions import NotFoundError, ProviderUnavailableError, ValidationError
from app.providers.base_provider import BaseProvider, ProviderResponse
from app.registry.model_registry import InMemoryModelRegistry, ModelRegistry


class InferenceService(ABC):
    """Application service that owns inference orchestration."""

    @abstractmethod
    async def complete(self, *, model_id: str, prompt: str, **kwargs: Any) -> ProviderResponse:
        """Generate a completion for the given model and prompt."""
        raise NotImplementedError

    @abstractmethod
    async def stream_completion(self, *, model_id: str, prompt: str, **kwargs: Any) -> AsyncIterator[str]:
        """Stream a completion for the given model and prompt."""
        raise NotImplementedError


class DefaultInferenceService(InferenceService):
    """Concrete inference service with provider selection and validation logic."""

    def __init__(self, registry: ModelRegistry, provider: BaseProvider) -> None:
        self._registry = registry
        self._provider = provider

    async def complete(self, *, model_id: str, prompt: str, **kwargs: Any) -> ProviderResponse:
        self._validate_request(model_id=model_id, prompt=prompt)

        try:
            response = await self._provider.generate(model=model_id, prompt=prompt, **kwargs)
        except Exception as exc:  # pragma: no cover - defensive boundary
            raise ProviderUnavailableError(f"Provider failed for model '{model_id}'") from exc

        return response

    async def stream_completion(self, *, model_id: str, prompt: str, **kwargs: Any) -> AsyncIterator[str]:
        self._validate_request(model_id=model_id, prompt=prompt)

        async def event_stream() -> AsyncIterator[str]:
            try:
                async for token in self._provider.stream(model=model_id, prompt=prompt, **kwargs):
                    payload = {
                        "id": f"chatcmpl-{model_id}",
                        "object": "chat.completion.chunk",
                        "created": int(time.time()),
                        "model": model_id,
                        "choices": [
                            {
                                "index": 0,
                                "delta": {"content": token},
                                "finish_reason": None,
                            }
                        ],
                    }
                    yield f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"
            except Exception as exc:  # pragma: no cover - defensive boundary
                raise ProviderUnavailableError(f"Provider failed for model '{model_id}'") from exc

            yield "data: [DONE]\n\n"

        async for chunk in event_stream():
            yield chunk

    def _validate_request(self, *, model_id: str, prompt: str) -> None:
        if not model_id or not prompt:
            raise ValidationError("model_id and prompt are required")

        model = self._registry.get_model(model_id)
        if model is None:
            raise NotFoundError(f"Model '{model_id}' was not found")

        if model.status != "available":
            raise ProviderUnavailableError(f"Model '{model_id}' is not available")


def build_inference_service(registry: ModelRegistry | None = None, provider: BaseProvider | None = None) -> InferenceService:
    """Create a service instance using dependency injection-friendly defaults."""
    if registry is None:
        registry = InMemoryModelRegistry()
    if provider is None:
        from app.providers.openai_provider import OpenAIProvider

        provider = OpenAIProvider()
    return DefaultInferenceService(registry=registry, provider=provider)
