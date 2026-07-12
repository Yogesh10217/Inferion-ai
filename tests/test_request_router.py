import pytest

from app.core.exceptions import ModelNotFoundException, ProviderNotFoundException, RoutingException
from app.providers.openai_provider import OpenAIProvider
from app.providers.provider_factory import ProviderFactory
from app.registry.model_registry import InMemoryModelRegistry
from app.routing.model_strategy import ModelBasedRoutingStrategy
from app.routing.request_router import RequestRouter, RoutingRequest


@pytest.mark.asyncio
async def test_request_router_routes_known_model_to_provider() -> None:
    registry = InMemoryModelRegistry()
    router = RequestRouter(
        registry=registry,
        strategy=ModelBasedRoutingStrategy(),
        provider_factory=ProviderFactory(),
    )

    provider = await router.route(RoutingRequest(model_id="gpt-4o-mini"))

    assert isinstance(provider, OpenAIProvider)


@pytest.mark.asyncio
async def test_request_router_raises_for_unknown_model() -> None:
    registry = InMemoryModelRegistry()
    router = RequestRouter(
        registry=registry,
        strategy=ModelBasedRoutingStrategy(),
        provider_factory=ProviderFactory(),
    )

    with pytest.raises(ModelNotFoundException):
        await router.route(RoutingRequest(model_id="missing-model"))


@pytest.mark.asyncio
async def test_request_router_raises_when_provider_missing() -> None:
    class MissingProviderStrategy(ModelBasedRoutingStrategy):
        async def determine_provider_name(self, *, model, request):
            return "missing-provider"

    registry = InMemoryModelRegistry()
    router = RequestRouter(
        registry=registry,
        strategy=MissingProviderStrategy(),
        provider_factory=ProviderFactory(),
    )

    with pytest.raises(ProviderNotFoundException):
        await router.route(RoutingRequest(model_id="gpt-4o-mini"))


@pytest.mark.asyncio
async def test_request_router_accepts_custom_strategy() -> None:
    class CustomStrategy(ModelBasedRoutingStrategy):
        async def determine_provider_name(self, *, model, request):
            return "ollama"

    registry = InMemoryModelRegistry()
    router = RequestRouter(
        registry=registry,
        strategy=CustomStrategy(),
        provider_factory=ProviderFactory(),
    )

    provider = await router.route(RoutingRequest(model_id="gpt-4o-mini"))

    assert provider.name == "ollama"
