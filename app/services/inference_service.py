from __future__ import annotations

import json
import time
from abc import ABC, abstractmethod
from typing import Any, AsyncIterator

from app.adapters.openai_response_adapter import OpenAIResponseAdapter
from app.core.exceptions import NotFoundError, ProviderUnavailableError, ValidationError
from app.providers.base_provider import BaseProvider
from app.registry.model_registry import InMemoryModelRegistry, ModelRegistry
from app.routing.request_router import RequestRouter, RoutingRequest
from app.schemas.inference_response import InferenceResponse
from app.schemas.request import ChatMessage, InferenceRequest
from app.schemas.response import ChatCompletionResponse


class InferenceService(ABC):
    """Application service that owns inference orchestration."""

    @abstractmethod
    async def complete(self, *, model_id: str, prompt: str, **kwargs: Any) -> InferenceResponse:
        """Generate a completion for the given model and prompt."""
        raise NotImplementedError

    @abstractmethod
    async def stream_completion(self, *, model_id: str, prompt: str, **kwargs: Any) -> AsyncIterator[str]:
        """Stream a completion for the given model and prompt."""
        raise NotImplementedError


class DefaultInferenceService(InferenceService):
    """Concrete inference service with provider selection and validation logic."""

    def __init__(self, registry: ModelRegistry, provider: BaseProvider | None = None, request_router: RequestRouter | None = None, response_adapter: OpenAIResponseAdapter | None = None) -> None:
        self._registry = registry
        self._provider = provider
        self._request_router = request_router
        self._response_adapter = response_adapter or OpenAIResponseAdapter()

    async def complete(self, *, model_id: str, prompt: str, **kwargs: Any) -> InferenceResponse:
        self._validate_request(model_id=model_id, prompt=prompt)

        provider = await self._resolve_provider(model_id=model_id)
        request = self._build_request(model_id=model_id, prompt=prompt, **kwargs)

        try:
            response = await provider.generate(request=request)
        except Exception as exc:  # pragma: no cover - defensive boundary
            raise ProviderUnavailableError(f"Provider failed for model '{model_id}'") from exc

        return response

    async def stream_completion(self, *, model_id: str, prompt: str, **kwargs: Any) -> AsyncIterator[str]:
        self._validate_request(model_id=model_id, prompt=prompt)
        provider = await self._resolve_provider(model_id=model_id)
        request = self._build_request(model_id=model_id, prompt=prompt, **kwargs)

        async def event_stream() -> AsyncIterator[str]:
            try:
                async for token in provider.stream(request=request):
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

    def _build_request(self, *, model_id: str, prompt: str, **kwargs: Any) -> InferenceRequest:
        return InferenceRequest(
            model=model_id,
            messages=[ChatMessage(role="user", content=prompt)],
            temperature=kwargs.get("temperature"),
            top_p=kwargs.get("top_p"),
            max_tokens=kwargs.get("max_tokens"),
            stream=kwargs.get("stream", False),
            stop=kwargs.get("stop"),
            frequency_penalty=kwargs.get("frequency_penalty"),
            presence_penalty=kwargs.get("presence_penalty"),
            metadata=kwargs.get("metadata"),
        )

    async def _resolve_provider(self, *, model_id: str) -> BaseProvider:
        if self._request_router is not None:
            return await self._request_router.route(RoutingRequest(model_id=model_id))
        if self._provider is None:
            raise ProviderUnavailableError(f"No provider configured for model '{model_id}'")
        return self._provider


def build_inference_service(
    registry: ModelRegistry | None = None,
    provider: BaseProvider | None = None,
    request_router: RequestRouter | None = None,
    response_adapter: OpenAIResponseAdapter | None = None,
) -> InferenceService:
    """Create a service instance using dependency injection-friendly defaults."""
    if registry is None:
        registry = InMemoryModelRegistry()
    if request_router is None and provider is None:
        from app.routing.model_strategy import ModelBasedRoutingStrategy

        request_router = RequestRouter(
            registry=registry,
            strategy=ModelBasedRoutingStrategy(),
        )
    if provider is not None:
        return DefaultInferenceService(registry=registry, provider=provider, request_router=request_router, response_adapter=response_adapter)
    return DefaultInferenceService(registry=registry, provider=None, request_router=request_router, response_adapter=response_adapter)
