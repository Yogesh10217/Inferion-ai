import pytest

from app.core.exceptions import NotFoundError, ProviderUnavailableError, ValidationError
from app.providers.openai_provider import OpenAIProvider
from app.registry.model_registry import InMemoryModelRegistry
from app.registry.model_metadata import RegisteredModel
from app.services.inference_service import DefaultInferenceService


from app.routing.request_router import RequestRouter
from app.routing.model_strategy import ModelBasedRoutingStrategy
from app.services.metrics_service import MetricsService
from app.services.request_scheduler import RequestScheduler
from app.providers.provider_factory import ProviderFactory

class DirectExecuteBatchCollector:
    def __init__(self, provider):
        self.provider = provider
        
    async def add_entry(self, entry):
        res = await self.provider.generate(request=entry.request)
        entry.result_future.set_result(res)

@pytest.mark.asyncio
async def test_complete_returns_standardized_response_for_known_model() -> None:
    registry = InMemoryModelRegistry()
    provider_factory = ProviderFactory()
    
    # We will pass a mocked routing strategy just to use our provider directly
    router = RequestRouter(registry=registry, strategy=ModelBasedRoutingStrategy())
    provider = provider_factory.get_provider("openai")
    
    collector = DirectExecuteBatchCollector(provider)
    scheduler = RequestScheduler(router=router, metrics=MetricsService(), batch_collector=collector)
    service = DefaultInferenceService(registry=registry, request_router=router, request_scheduler=scheduler)

    response = await service.complete(model_id="gpt-4o-mini", prompt="Hello")

    assert response.model == "gpt-4o-mini"
    assert response.provider == "openai"
    assert "Hello" in response.text


@pytest.mark.asyncio
async def test_complete_raises_for_unknown_model() -> None:
    registry = InMemoryModelRegistry()
    service = DefaultInferenceService(registry=registry, provider=OpenAIProvider())

    with pytest.raises(NotFoundError):
        await service.complete(model_id="missing-model", prompt="Hello")


@pytest.mark.asyncio
async def test_complete_raises_for_empty_prompt() -> None:
    registry = InMemoryModelRegistry()
    service = DefaultInferenceService(registry=registry, provider=OpenAIProvider())

    with pytest.raises(ValidationError):
        await service.complete(model_id="gpt-4o-mini", prompt="")


@pytest.mark.asyncio
async def test_complete_raises_when_model_status_is_not_available() -> None:
    registry = InMemoryModelRegistry()
    registry.register_model(
        RegisteredModel(
            id="gpt-4o-mini",
            provider="openai",
            description="test",
            context_window=128000,
            status="degraded",
        )
    )
    service = DefaultInferenceService(registry=registry, provider=OpenAIProvider())

    with pytest.raises(ProviderUnavailableError):
        await service.complete(model_id="gpt-4o-mini", prompt="Hello")
