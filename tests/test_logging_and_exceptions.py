from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_standardized_error_payload() -> None:
    response = client.get("/v1/models")
    assert response.status_code == 200


def test_invalid_request_exception_payload() -> None:
    response = client.post(
        "/v1/chat/completions",
        json={"messages": [{"role": "user", "content": "Hello"}]},
    )
    assert response.status_code == 422
    body = response.json()
    assert "detail" in body


def test_logging_middleware_sets_request_id() -> None:
    response = client.get("/v1/health", headers={"x-request-id": "req-123"})
    assert response.status_code == 200
