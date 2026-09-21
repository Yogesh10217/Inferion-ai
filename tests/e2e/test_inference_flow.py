import json

import pytest


@pytest.mark.asyncio
async def test_e2e_non_streaming_chat_completion(get_client, admin_token_headers):
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello world"},
        ],
        "metadata": {"mock": True},
    }

    async with get_client() as client:
        response = await client.post("/v1/chat/completions", json=payload, headers=admin_token_headers)
        assert response.status_code == 200

        data = response.json()
        assert data["object"] == "chat.completion"
        assert data["model"] == "gpt-4o-mini"
        assert len(data["choices"]) > 0
        assert "Hello world" in data["choices"][0]["message"]["content"]
        assert "usage" in data
        assert data["usage"]["total_tokens"] > 0


@pytest.mark.asyncio
async def test_e2e_streaming_chat_completion(get_client, admin_token_headers):
    payload = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": "Stream test"}],
        "stream": True,
        "metadata": {"mock": True},
    }

    async with get_client() as client:
        response = await client.post("/v1/chat/completions", json=payload, headers=admin_token_headers)
        assert response.status_code == 200
        assert "text/event-stream" in response.headers.get("content-type", "")

        lines = response.text.split("\n")
        chunks = []
        has_done = False

        for line in lines:
            line = line.strip()
            if line.startswith("data: "):
                data_content = line[6:].strip()
                if data_content == "[DONE]":
                    has_done = True
                    break
                try:
                    chunk = json.loads(data_content)
                    chunks.append(chunk)
                except json.JSONDecodeError:
                    pass

        assert len(chunks) > 0
        assert has_done is True


@pytest.mark.asyncio
async def test_e2e_inference_service_direct_generation():
    from app.core.container import ServiceContainer
    from app.schemas.request import ChatMessage, InferenceRequest

    container = ServiceContainer()
    req = InferenceRequest(
        model="gpt-4o-mini",
        messages=[ChatMessage(role="user", content="Direct generation test")],
        metadata={"mock": True},
    )

    response = await container.inference_service.generate(req)
    assert response.provider == "openai"
    assert response.model == "gpt-4o-mini"
    assert "Direct generation test" in response.text
