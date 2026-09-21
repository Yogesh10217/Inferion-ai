from unittest.mock import AsyncMock

import pytest

from app.providers.ollama_provider import OllamaProvider
from app.providers.openai_provider import OpenAIProvider
from app.registry.model_registry import InMemoryModelRegistry
from app.routing.request_router import RoutingDecision
from app.services.inference_service import DefaultInferenceService
from app.services.metrics_service import MetricsService
from app.services.request_scheduler import RequestScheduler


@pytest.mark.asyncio
async def test_openai_provider_generate_can_be_mocked() -> None:
    provider = OpenAIProvider()
    provider.generate = AsyncMock(
        return_value=type("Response", (), {"text": "mock", "model": "gpt-4o-mini", "provider": "openai"})()
    )

    response = await provider.generate(model="gpt-4o-mini", prompt="Hello")
    assert response.text == "mock"


@pytest.mark.asyncio
async def test_ollama_provider_generate_can_be_mocked() -> None:
    provider = OllamaProvider()
    provider.generate = AsyncMock(
        return_value=type("Response", (), {"text": "ollama-mock", "model": "llama3.1", "provider": "ollama"})()
    )

    response = await provider.generate(model="llama3.1", prompt="Hello")
    assert response.text == "ollama-mock"


class DirectExecuteBatchCollector:
    def __init__(self, provider):
        self.provider = provider

    async def add_entry(self, entry):
        res = await self.provider.generate(request=entry.request)
        entry.result_future.set_result(res)


@pytest.mark.asyncio
async def test_inference_service_uses_mock_provider() -> None:
    registry = InMemoryModelRegistry()
    provider = AsyncMock()
    provider.generate.return_value = type(
        "Response", (), {"text": "mocked", "model": "gpt-4o-mini", "provider": "openai"}
    )()

    router = AsyncMock()
    router.route.return_value = RoutingDecision(provider_id="mock", model_id="gpt-4o-mini")

    collector = DirectExecuteBatchCollector(provider)
    scheduler = RequestScheduler(router=router, metrics=MetricsService(), batch_collector=collector)

    service = DefaultInferenceService(registry=registry, request_router=router, request_scheduler=scheduler)

    response = await service.complete(model_id="gpt-4o-mini", prompt="Hello")
    assert response.text == "mocked"
    provider.generate.assert_awaited_once()

