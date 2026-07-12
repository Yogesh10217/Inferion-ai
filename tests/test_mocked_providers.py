from unittest.mock import AsyncMock, patch

import pytest

from app.providers.openai_provider import OpenAIProvider
from app.providers.ollama_provider import OllamaProvider
from app.services.inference_service import DefaultInferenceService
from app.registry.model_registry import InMemoryModelRegistry


@pytest.mark.asyncio
async def test_openai_provider_generate_can_be_mocked() -> None:
    provider = OpenAIProvider()
    provider.generate = AsyncMock(return_value=type("Response", (), {"text": "mock", "model": "gpt-4o-mini", "provider": "openai"})())

    response = await provider.generate(model="gpt-4o-mini", prompt="Hello")
    assert response.text == "mock"


@pytest.mark.asyncio
async def test_ollama_provider_generate_can_be_mocked() -> None:
    provider = OllamaProvider()
    provider.generate = AsyncMock(return_value=type("Response", (), {"text": "ollama-mock", "model": "llama3.1", "provider": "ollama"})())

    response = await provider.generate(model="llama3.1", prompt="Hello")
    assert response.text == "ollama-mock"


@pytest.mark.asyncio
async def test_inference_service_uses_mock_provider() -> None:
    registry = InMemoryModelRegistry()
    provider = AsyncMock()
    provider.generate.return_value = type("Response", (), {"text": "mocked", "model": "gpt-4o-mini", "provider": "openai"})()
    service = DefaultInferenceService(registry=registry, provider=provider)

    response = await service.complete(model_id="gpt-4o-mini", prompt="Hello")
    assert response.text == "mocked"
    provider.generate.assert_awaited_once()
