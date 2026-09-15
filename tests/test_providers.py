import pytest

from app.providers.anthropic_provider import AnthropicProvider
from app.providers.base_provider import ProviderModel
from app.providers.cohere_provider import CohereProvider
from app.providers.gemini_provider import GeminiProvider
from app.providers.mistral_provider import MistralProvider
from app.providers.ollama_provider import OllamaProvider
from app.providers.openai_provider import OpenAIProvider
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
async def test_anthropic_provider_mock() -> None:
    provider = AnthropicProvider(api_key="mock-key")
    response = await provider.generate(model="claude-3-5-sonnet-20241022", prompt="Hello Claude")

    assert isinstance(response, InferenceResponse)
    assert response.provider == "anthropic"
    assert "Hello Claude" in response.text
    assert await provider.health_check() is True
    models = await provider.list_models()
    assert len(models) >= 3


@pytest.mark.asyncio
async def test_gemini_provider_mock() -> None:
    provider = GeminiProvider(api_key="mock-key")
    response = await provider.generate(model="gemini-1.5-flash", prompt="Hello Gemini")

    assert isinstance(response, InferenceResponse)
    assert response.provider == "gemini"
    assert "Hello Gemini" in response.text
    assert await provider.health_check() is True
    models = await provider.list_models()
    assert len(models) >= 2


@pytest.mark.asyncio
async def test_cohere_provider_mock() -> None:
    provider = CohereProvider(api_key="mock-key")
    response = await provider.generate(model="command-r-plus", prompt="Hello Cohere")

    assert isinstance(response, InferenceResponse)
    assert response.provider == "cohere"
    assert "Hello Cohere" in response.text
    assert await provider.health_check() is True
    models = await provider.list_models()
    assert len(models) >= 2


@pytest.mark.asyncio
async def test_mistral_provider_mock() -> None:
    provider = MistralProvider(api_key="mock-key")
    response = await provider.generate(model="mistral-large-latest", prompt="Hello Mistral")

    assert isinstance(response, InferenceResponse)
    assert response.provider == "mistral"
    assert "Hello Mistral" in response.text
    assert await provider.health_check() is True
    models = await provider.list_models()
    assert len(models) >= 3


@pytest.mark.asyncio
async def test_ollama_provider_health_and_models() -> None:
    provider = OllamaProvider(base_url="mock")

    assert await provider.health_check() is True
    models = await provider.list_models()
    assert isinstance(models[0], ProviderModel)
    assert models[0].provider == "ollama"


@pytest.mark.asyncio
async def test_provider_stream_is_async_iterable() -> None:
    provider = OpenAIProvider(api_key="test-key")
    stream = [chunk async for chunk in provider.stream(model="gpt-4o-mini", prompt="Hello")]

    assert all(isinstance(chunk, InferenceResponse) for chunk in stream)
    assert stream[-1].finish_reason == "stop"
    assert any("Hello" in chunk.text for chunk in stream)
