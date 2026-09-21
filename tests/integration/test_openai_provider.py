from unittest.mock import patch

import httpx
import pytest

from app.core.exceptions import ProviderUnavailableException
from app.providers.openai_provider import OpenAIProvider
from app.schemas.inference_response import InferenceResponse
from app.schemas.request import ChatMessage, InferenceRequest


@pytest.mark.asyncio
async def test_openai_provider_real_http_success_parsing():
    provider = OpenAIProvider(api_key="real-sk-key-test")

    mock_response_json = {
        "id": "chatcmpl-999",
        "model": "gpt-4o-mini",
        "choices": [
            {"message": {"role": "assistant", "content": "Hello from mock OpenAI API"}, "finish_reason": "stop"}
        ],
        "usage": {"prompt_tokens": 5, "completion_tokens": 6, "total_tokens": 11},
        "created": 1700000000,
    }

    def custom_handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=mock_response_json)

    transport = httpx.MockTransport(custom_handler)
    client = httpx.AsyncClient(transport=transport)

    with patch("app.providers.openai_provider.httpx.AsyncClient", return_value=client):
        req = InferenceRequest(model="gpt-4o-mini", messages=[ChatMessage(role="user", content="Hi")])
        res = await provider.generate(request=req)

        assert isinstance(res, InferenceResponse)
        assert res.provider == "openai"
        assert res.model == "gpt-4o-mini"
        assert res.text == "Hello from mock OpenAI API"
        assert res.usage.total_tokens == 11


@pytest.mark.asyncio
async def test_openai_provider_error_status_handling():
    provider = OpenAIProvider(api_key="real-sk-key-test")

    def error_handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(401, json={"error": {"message": "Invalid API key"}})

    transport = httpx.MockTransport(error_handler)
    client = httpx.AsyncClient(transport=transport)

    with patch("app.providers.openai_provider.httpx.AsyncClient", return_value=client):
        req = InferenceRequest(model="gpt-4o-mini", messages=[ChatMessage(role="user", content="Hi")])
        with pytest.raises(ProviderUnavailableException) as exc_info:
            await provider.generate(request=req)

        assert "OpenAI error status 401" in str(exc_info.value)
