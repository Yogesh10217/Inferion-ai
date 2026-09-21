import json
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from app.core.exceptions import ProviderUnavailableException
from app.providers.ollama_provider import OllamaProvider
from app.providers.openai_provider import OpenAIProvider
from app.schemas.request import ChatMessage, InferenceRequest


class MockStreamContext:
    def __init__(self, response):
        self.response = response

    async def __aenter__(self):
        return self.response

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


class MockAsyncClient:
    def __init__(self, response=None, error_on_stream=None):
        self.response = response
        self.error_on_stream = error_on_stream

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    def stream(self, *args, **kwargs):
        if self.error_on_stream:
            raise self.error_on_stream
        return MockStreamContext(self.response)


def create_mock_client(
    status_code: int = 200,
    content_lines: list[str] | None = None,
    error_on_stream: Exception | None = None,
    error_body: bytes = b"",
):
    mock_response = MagicMock()
    mock_response.status_code = status_code

    if error_body:
        mock_response.aread = AsyncMock(return_value=error_body)

    if content_lines is not None:

        async def mock_iter_lines():
            for line in content_lines:
                yield line

        mock_response.aiter_lines = mock_iter_lines

    return MockAsyncClient(response=mock_response, error_on_stream=error_on_stream)


@pytest.mark.asyncio
async def test_streaming_endpoint_returns_openai_sse_format(get_client, admin_token_headers: dict) -> None:
    payload = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": "Hello world"}],
        "stream": True,
    }
    async with get_client() as client:
        response = await client.post("/v1/chat/completions", json=payload, headers=admin_token_headers)
        assert response.status_code == 200
    assert "text/event-stream" in response.headers["content-type"].lower()

    lines = response.text.split("\n")
    data_lines = [line for line in lines if line.startswith("data: ")]
    assert len(data_lines) > 0
    assert data_lines[-1] == "data: [DONE]"

    first_chunk_json = data_lines[0][len("data: ") :]
    chunk_data = json.loads(first_chunk_json)
    assert chunk_data["object"] == "chat.completion.chunk"
    assert chunk_data["model"] == "gpt-4o-mini"
    assert "choices" in chunk_data
    assert len(chunk_data["choices"]) > 0


@pytest.mark.asyncio
async def test_openai_real_streaming_decoding() -> None:
    provider = OpenAIProvider(api_key="real-key-pattern")

    lines = [
        'data: {"id":"chatcmpl-1","object":"chat.completion.chunk","created":12345,"model":"gpt-4o-mini","choices":[{"index":0,"delta":{"content":"Hello"},"finish_reason":null}]}',
        "",
        'data: {"id":"chatcmpl-1","object":"chat.completion.chunk","created":12345,"model":"gpt-4o-mini","choices":[{"index":0,"delta":{"content":" world"},"finish_reason":"stop"}]}',
        "data: [DONE]",
    ]
    mock_client = create_mock_client(status_code=200, content_lines=lines)

    with patch("httpx.AsyncClient", return_value=mock_client):
        request = InferenceRequest(
            model="gpt-4o-mini",
            messages=[ChatMessage(role="user", content="Hello")],
        )
        chunks = []
        async for chunk in provider.stream(request):
            chunks.append(chunk)

        assert len(chunks) == 2
        assert chunks[0].text == "Hello"
        assert chunks[0].finish_reason == ""
        assert chunks[1].text == " world"
        assert chunks[1].finish_reason == "stop"
        assert chunks[0].model == "gpt-4o-mini"
        assert chunks[0].provider == "openai"


@pytest.mark.asyncio
async def test_ollama_real_streaming_decoding() -> None:
    provider = OllamaProvider(base_url="http://real-ollama-url")

    lines = [
        '{"model":"llama3.1","created_at":"2026-07-14T12:00:00Z","message":{"role":"assistant","content":"First"},"done":false}',
        '{"model":"llama3.1","created_at":"2026-07-14T12:00:01Z","message":{"role":"assistant","content":"Second"},"done":true,"done_reason":"stop","prompt_eval_count":10,"eval_count":20}',
    ]
    mock_client = create_mock_client(status_code=200, content_lines=lines)

    with patch("httpx.AsyncClient", return_value=mock_client):
        request = InferenceRequest(
            model="llama3.1",
            messages=[ChatMessage(role="user", content="Hi")],
        )
        chunks = []
        async for chunk in provider.stream(request):
            chunks.append(chunk)

        assert len(chunks) == 2
        assert chunks[0].text == "First"
        assert chunks[0].finish_reason == ""
        assert chunks[1].text == "Second"
        assert chunks[1].finish_reason == "stop"
        assert chunks[1].usage.prompt_tokens == 10
        assert chunks[1].usage.completion_tokens == 20
        assert chunks[1].usage.total_tokens == 30


@pytest.mark.asyncio
async def test_streaming_chunk_ordering() -> None:
    provider = OpenAIProvider()
    request = InferenceRequest(
        model="gpt-4o-mini",
        messages=[ChatMessage(role="user", content="First second third")],
    )
    chunks = []
    async for chunk in provider.stream(request):
        chunks.append(chunk.text)

    expected_words = "[openai:gpt-4o-mini] First second third".split()
    assert len(chunks) == len(expected_words)
    for idx, expected in enumerate(expected_words):
        suffix = " " if idx < len(expected_words) - 1 else ""
        assert chunks[idx] == expected + suffix


@pytest.mark.asyncio
async def test_streaming_error_handling_http_status() -> None:
    provider = OpenAIProvider(api_key="real-key")
    mock_client = create_mock_client(status_code=401, error_body=b"Unauthorized access")

    with patch("httpx.AsyncClient", return_value=mock_client):
        request = InferenceRequest(
            model="gpt-4o-mini",
            messages=[ChatMessage(role="user", content="Hello")],
        )
        with pytest.raises(ProviderUnavailableException) as excinfo:
            async for _ in provider.stream(request):
                pass
        assert "401" in str(excinfo.value)
        assert "Unauthorized" in str(excinfo.value)


@pytest.mark.asyncio
async def test_streaming_error_handling_connection_error() -> None:
    provider = OllamaProvider(base_url="http://localhost:11434")
    mock_client = create_mock_client(error_on_stream=httpx.ConnectError("Connection refused"))

    with patch("httpx.AsyncClient", return_value=mock_client):
        request = InferenceRequest(
            model="llama3.1",
            messages=[ChatMessage(role="user", content="Hi")],
        )
        with pytest.raises(ProviderUnavailableException) as excinfo:
            async for _ in provider.stream(request):
                pass
        assert "connection error" in str(excinfo.value)


@pytest.mark.asyncio
async def test_streaming_cancellation() -> None:
    provider = OpenAIProvider()
    request = InferenceRequest(
        model="gpt-4o-mini",
        messages=[ChatMessage(role="user", content="Short prompt")],
    )

    iterator = provider.stream(request)
    first_chunk = await anext(iterator)
    assert first_chunk is not None

    await iterator.aclose()

    with pytest.raises(StopAsyncIteration):
        await anext(iterator)
