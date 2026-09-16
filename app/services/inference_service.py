from __future__ import annotations

import json
import time
from abc import ABC, abstractmethod
from typing import Any, AsyncIterator

from app.adapters.openai_response_adapter import OpenAIResponseAdapter
from app.core.exceptions import AppException, NotFoundError, ProviderUnavailableError, ValidationError
from app.limits.events import UsageEvent, UsageEventEmitter
from app.providers.base_provider import BaseProvider
from app.registry.model_registry import InMemoryModelRegistry, ModelRegistry
from app.routing.request_router import RequestRouter, RoutingRequest
from app.schemas.inference_response import InferenceResponse
from app.schemas.request import ChatMessage, InferenceRequest
from app.services.request_scheduler import RequestScheduler
from app.services.streaming_manager import StreamingManager
from app.tracing.tracer import get_tracer

_tracer = get_tracer("inference_service")


class InferenceService(ABC):
    """Application service that owns inference orchestration."""

    @abstractmethod
    async def complete(self, *, model_id: str, prompt: str, **kwargs: Any) -> InferenceResponse:
        """Generate a completion for the given model and prompt."""
        raise NotImplementedError

    @abstractmethod
    async def generate(self, request: InferenceRequest) -> InferenceResponse:
        """Generate a completion directly for the given InferenceRequest."""
        raise NotImplementedError

    @abstractmethod
    async def stream_completion(self, *, model_id: str, prompt: str, **kwargs: Any) -> AsyncIterator[str]:
        """Stream a completion for the given model and prompt."""
        raise NotImplementedError

    @abstractmethod
    async def stream(self, request: InferenceRequest) -> AsyncIterator[InferenceResponse]:
        """Stream a completion returning InferenceResponse chunks."""
        raise NotImplementedError


class DefaultInferenceService(InferenceService):
    """Concrete inference service with provider selection and validation logic."""

    def __init__(
        self,
        registry: ModelRegistry,
        provider: BaseProvider | None = None,
        request_router: RequestRouter | None = None,
        response_adapter: OpenAIResponseAdapter | None = None,
        streaming_manager: StreamingManager | None = None,
        request_scheduler: RequestScheduler | None = None,
        usage_emitter: UsageEventEmitter | None = None,
    ) -> None:
        self._registry = registry
        self._provider = provider
        self._request_router = request_router
        self._response_adapter = response_adapter or OpenAIResponseAdapter()
        self._streaming_manager = streaming_manager or StreamingManager()
        self._request_scheduler = request_scheduler
        self._usage_emitter = usage_emitter

    async def complete(self, *, model_id: str, prompt: str, **kwargs: Any) -> InferenceResponse:
        with _tracer.start_span("inference.complete", attributes={"model_id": model_id}):
            self._validate_request(model_id=model_id, prompt=prompt)

            request = self._build_request(model_id=model_id, prompt=prompt, **kwargs)

            if self._request_scheduler is None:
                raise RuntimeError("RequestScheduler not configured")

            start_time = time.time()
            try:
                response = await self._request_scheduler.generate(request=request)
                duration_ms = int((time.time() - start_time) * 1000)

                if self._usage_emitter:
                    self._usage_emitter.emit(UsageEvent(
                        organization_id=kwargs.get("organization_id", "default"),
                        workspace_id=kwargs.get("workspace_id"),
                        user_id=kwargs.get("user_id"),
                        api_key_id=kwargs.get("api_key_id"),
                        provider=response.model.split('/')[0] if '/' in response.model else "unknown",
                        model=response.model,
                        request_tokens=response.usage.prompt_tokens if response.usage else 0,
                        response_tokens=response.usage.completion_tokens if response.usage else 0,
                        status_code="200",
                        is_streaming=False,
                        is_cached=False,  # Can extract from response if metadata supports it
                        duration_ms=duration_ms
                    ))

            except Exception as exc:  # pragma: no cover - defensive boundary
                duration_ms = int((time.time() - start_time) * 1000)
                if self._usage_emitter:
                    self._usage_emitter.emit(UsageEvent(
                        organization_id=kwargs.get("organization_id", "default"),
                        workspace_id=kwargs.get("workspace_id"),
                        user_id=kwargs.get("user_id"),
                        api_key_id=kwargs.get("api_key_id"),
                        provider="unknown",
                        model=model_id,
                        status_code="500",
                        error_type=type(exc).__name__,
                        duration_ms=duration_ms
                    ))
                raise ProviderUnavailableError(f"Provider failed for model '{model_id}'") from exc

            return response

    async def generate(self, request: InferenceRequest) -> InferenceResponse:
        model_id = request.model
        prompt = self._extract_prompt_from_request(request)
        return await self.complete(
            model_id=model_id,
            prompt=prompt,
            temperature=request.temperature,
            top_p=request.top_p,
            max_tokens=request.max_tokens,
            stream=request.stream,
            stop=request.stop,
            frequency_penalty=request.frequency_penalty,
            presence_penalty=request.presence_penalty,
            metadata=request.metadata,
        )

    async def stream_completion(self, *, model_id: str, prompt: str, **kwargs: Any) -> AsyncIterator[str]:
        self._validate_request(model_id=model_id, prompt=prompt)
        request = self._build_request(model_id=model_id, prompt=prompt, **kwargs)

        async def event_stream() -> AsyncIterator[str]:
            try:
                async for chunk in self.stream(request=request):
                    payload = {
                        "id": chunk.id,
                        "object": "chat.completion.chunk",
                        "created": int(chunk.created.timestamp()),
                        "model": chunk.model,
                        "choices": [
                            {
                                "index": 0,
                                "delta": {"content": chunk.text} if chunk.text else {},
                                "finish_reason": chunk.finish_reason or None,
                            }
                        ],
                    }
                    yield f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"
            except Exception as exc:
                if isinstance(exc, AppException):
                    raise exc
                raise ProviderUnavailableError(f"Provider failed for model '{model_id}'") from exc

            yield "data: [DONE]\n\n"

        async for chunk in event_stream():
            yield chunk

    async def stream(self, request: InferenceRequest) -> AsyncIterator[InferenceResponse]:
        self._validate_request(model_id=request.model, prompt=self._extract_prompt_from_request(request))
        try:
            async for chunk in self._streaming_manager.stream(request=request):
                yield chunk
        except Exception as exc:
            if isinstance(exc, AppException):
                raise exc
            raise ProviderUnavailableError(f"Provider failed for model '{request.model}'") from exc

    def _extract_prompt_from_request(self, request: InferenceRequest) -> str:
        if not request.messages:
            return ""
        return request.messages[-1].content

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
    streaming_manager: StreamingManager | None = None,
    request_scheduler: RequestScheduler | None = None,
    usage_emitter: UsageEventEmitter | None = None,
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
    return DefaultInferenceService(
        registry=registry,
        provider=provider,
        request_router=request_router,
        response_adapter=response_adapter,
        streaming_manager=streaming_manager,
        request_scheduler=request_scheduler,
        usage_emitter=usage_emitter,
    )
