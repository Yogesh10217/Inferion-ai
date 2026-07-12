import pytest

from app.providers.base_provider import ProviderModel
from app.providers.openai_provider import OpenAIProvider
from app.providers.ollama_provider import OllamaProvider
from app.schemas.inference_response import InferenceResponse


@pytest.mark.asyncio
async def test_openai_provider_generate_returns_standardized_response() -> None:
    provider = OpenAIProvider(api_key="test-key")
    response = await provider.generate(model="gpt-4o-mini", prompt="Hello")

    assert isinstance(response, InferenceResponse)
    assert response.provider == "openai"
    assert response.model == "gpt-4o-mini"
    assert "Hello" in response.text


@pytest.mark.asyncio
async def test_ollama_provider_health_and_models() -> None:
    provider = OllamaProvider()

    assert await provider.health_check() is True
    models = await provider.list_models()
    assert isinstance(models[0], ProviderModel)
    assert models[0].provider == "ollama"


@pytest.mark.asyncio
async def test_provider_stream_is_async_iterable() -> None:
    provider = OpenAIProvider()
    stream = [chunk async for chunk in provider.stream(model="gpt-4o-mini", prompt="Hello")]

    assert stream[-1].startswith("data: [DONE]")
    assert any("chat.completion.chunk" in chunk for chunk in stream[:-1])
