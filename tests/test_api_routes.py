from unittest.mock import AsyncMock, patch

import pytest


@pytest.mark.asyncio
async def test_health_routes(get_client) -> None:
    async with get_client() as client:
        assert (await client.get("/v1/health")).status_code == 200
        assert (await client.get("/v1/ready")).status_code == 200
        assert (await client.get("/v1/live")).status_code == 200


@pytest.mark.asyncio
async def test_models_route_returns_openai_shape(get_client, admin_token_headers) -> None:
    async with get_client() as client:
        response = await client.get("/v1/models", headers=admin_token_headers)
        assert response.status_code == 200
        payload = response.json()
        assert payload["object"] == "list"
        assert isinstance(payload["data"], list)


@pytest.mark.asyncio
async def test_chat_completion_route_returns_openai_shape(get_client, admin_token_headers) -> None:
    payload = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": "Hello"}],
        "stream": False,
    }
    async with get_client() as client:
        response = await client.post("/v1/chat/completions", json=payload, headers=admin_token_headers)
        assert response.status_code == 200
        body = response.json()
        assert body["object"] == "chat.completion"
        assert body["model"] == "gpt-4o-mini"
        assert body["choices"][0]["message"]["content"]


@pytest.mark.asyncio
async def test_chat_completion_streaming_route_returns_sse_events(get_client, admin_token_headers) -> None:
    payload = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": "Hello"}],
        "stream": True,
    }
    async with get_client() as client:
        response = await client.post("/v1/chat/completions", json=payload, headers=admin_token_headers)
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/event-stream")
        text = response.text
        assert "data:" in text
        assert "[DONE]" in text


@pytest.mark.asyncio
async def test_chat_completion_route_uses_mocked_openai_provider(get_client, admin_token_headers) -> None:
    with patch(
        "app.services.inference_service.DefaultInferenceService.complete", new_callable=AsyncMock
    ) as mocked_complete:
        mocked_complete.return_value = type(
            "Response",
            (),
            {"text": "mocked", "model": "gpt-4o-mini", "provider": "openai", "finish_reason": "stop"},
        )()

        payload = {
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": "Hello"}],
            "stream": False,
        }
        async with get_client() as client:
            response = await client.post("/v1/chat/completions", json=payload, headers=admin_token_headers)
            assert response.status_code == 200
            assert response.json()["choices"][0]["message"]["content"] == "mocked"
