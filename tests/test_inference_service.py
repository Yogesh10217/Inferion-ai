import pytest

from app.core.exceptions import NotFoundError, ProviderUnavailableError, ValidationError
from app.providers.openai_provider import OpenAIProvider
from app.registry.model_registry import InMemoryModelRegistry
from app.registry.model_metadata import RegisteredModel
from app.services.inference_service import DefaultInferenceService


@pytest.mark.asyncio
async def test_complete_returns_standardized_response_for_known_model() -> None:
    registry = InMemoryModelRegistry()
    service = DefaultInferenceService(registry=registry, provider=OpenAIProvider())

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
