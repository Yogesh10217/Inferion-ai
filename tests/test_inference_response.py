import pytest

from app.adapters.openai_response_adapter import OpenAIResponseAdapter
from app.providers.openai_provider import OpenAIProvider
from app.providers.ollama_provider import OllamaProvider
from app.schemas.inference_response import InferenceResponse, Usage


def test_inference_response_validation() -> None:
    response = InferenceResponse(
        id="resp-1",
        provider="openai",
        model="gpt-4o-mini",
        text="hello",
        usage=Usage(prompt_tokens=3, completion_tokens=4, total_tokens=7),
        finish_reason="stop",
        latency_ms=12.5,
        metadata={"provider_version": "v1", "cached": False},
        request_id="req-1",
    )

    assert response.usage.total_tokens == 7
    assert response.metadata["cached"] is False


def test_openai_response_adapter_converts_to_chat_completion_shape() -> None:
    response = InferenceResponse(
        id="resp-1",
        provider="openai",
        model="gpt-4o-mini",
        text="hello",
        usage=Usage(prompt_tokens=3, completion_tokens=4, total_tokens=7),
        finish_reason="stop",
        latency_ms=12.5,
    )

    adapted = OpenAIResponseAdapter.to_chat_completion_response(response)

    assert adapted.model == "gpt-4o-mini"
    assert adapted.choices[0].message.content == "hello"
    assert adapted.usage.total_tokens == 7


@pytest.mark.asyncio
async def test_openai_provider_returns_inference_response() -> None:
    provider = OpenAIProvider()
    response = await provider.generate(request=None, model="gpt-4o-mini", prompt="Hello")
    assert isinstance(response, InferenceResponse)
    assert response.provider == "openai"


@pytest.mark.asyncio
async def test_ollama_provider_returns_inference_response() -> None:
    provider = OllamaProvider(base_url="mock")
    response = await provider.generate(request=None, model="llama3.1", prompt="Hello")
    assert isinstance(response, InferenceResponse)
    assert response.provider == "ollama"


def test_usage_serialization_and_metadata_preservation() -> None:
    response = InferenceResponse(
        id="resp-1",
        provider="openai",
        model="gpt-4o-mini",
        text="hello",
        usage=Usage(prompt_tokens=1, completion_tokens=2, total_tokens=3),
        metadata={"provider_version": "v1", "cached": False},
    )

    payload = response.model_dump()
    assert payload["usage"]["total_tokens"] == 3
    assert payload["metadata"]["cached"] is False


def test_latency_recording_defaults_to_non_negative_value() -> None:
    response = InferenceResponse(
        id="resp-1",
        provider="openai",
        model="gpt-4o-mini",
        text="hello",
    )
    assert response.latency_ms >= 0
