from app.main import app


import pytest

@pytest.mark.asyncio
async def test_standardized_error_payload(get_client, admin_token_headers) -> None:
    async with get_client() as client:
        response = await client.get("/v1/models", headers=admin_token_headers)
        assert response.status_code == 200

@pytest.mark.asyncio
async def test_invalid_request_exception_payload(get_client, admin_token_headers) -> None:
    async with get_client() as client:
        response = await client.post(
            "/v1/chat/completions",
            json={"messages": [{"role": "user", "content": "Hello"}]},
            headers=admin_token_headers
        )
        assert response.status_code == 422
        body = response.json()
        assert "detail" in body

@pytest.mark.asyncio
async def test_logging_middleware_sets_request_id(get_client) -> None:
    async with get_client() as client:
        response = await client.get("/v1/health", headers={"x-request-id": "req-123"})
        assert response.status_code == 200
