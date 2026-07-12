from typing import Iterator
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_routes() -> None:
    assert client.get("/v1/health").status_code == 200
    assert client.get("/v1/ready").status_code == 200
    assert client.get("/v1/live").status_code == 200


def test_models_route_returns_openai_shape() -> None:
    response = client.get("/v1/models")
    assert response.status_code == 200
    payload = response.json()
    assert payload["object"] == "list"
    assert isinstance(payload["data"], list)


def test_chat_completion_route_returns_openai_shape() -> None:
    payload = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": "Hello"}],
        "stream": False,
    }
    response = client.post("/v1/chat/completions", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["object"] == "chat.completion"
    assert body["model"] == "gpt-4o-mini"
    assert body["choices"][0]["message"]["content"]


def test_chat_completion_streaming_route_returns_sse_events() -> None:
    payload = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": "Hello"}],
        "stream": True,
    }
    response = client.post("/v1/chat/completions", json=payload)
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")
    text = response.text
    assert "data:" in text
    assert "[DONE]" in text


def test_chat_completion_route_uses_mocked_openai_provider() -> None:
    with patch("app.services.inference_service.DefaultInferenceService.complete") as mocked_complete:
        mocked_complete.return_value = type(
            "Response",
            (),
            {"text": "mocked", "model": "gpt-4o-mini", "provider": "openai"},
        )()
        payload = {
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": "Hello"}],
            "stream": False,
        }
        response = client.post("/v1/chat/completions", json=payload)
        assert response.status_code == 200
        assert response.json()["choices"][0]["message"]["content"] == "mocked"
