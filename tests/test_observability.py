from __future__ import annotations

import json
from datetime import datetime, timezone
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.metrics_service import MetricsService
from app.services.health_service import HealthService
from app.providers.provider_factory import ProviderFactory
from app.registry.model_registry import InMemoryModelRegistry
from app.core.exceptions import (
    ModelNotFoundException,
    ProviderNotFoundException,
    RoutingException,
    InferenceException,
    ProviderUnavailableException,
    ConfigurationException,
    ValidationException,
    AppExceptionHandler,
)


def test_metrics_service_direct() -> None:
    metrics = MetricsService()
    assert metrics.get_request_count() == 0
    assert metrics.get_error_count() == 0
    assert metrics.get_average_latency() == 0.0

    metrics.record_request(100.0, is_error=False)
    metrics.record_request(200.0, is_error=True)

    assert metrics.get_request_count() == 2
    assert metrics.get_error_count() == 1
    assert metrics.get_average_latency() == 150.0

    summary = metrics.get_metrics_summary()
    assert summary["request_count"] == 2
    assert summary["error_count"] == 1
    assert summary["average_latency_ms"] == 150.0


@pytest.mark.anyio
async def test_health_service_direct() -> None:
    factory = ProviderFactory()
    registry = InMemoryModelRegistry()
    metrics = MetricsService()
    startup_time = datetime.now(timezone.utc)
    app_version = "1.2.3"

    service = HealthService(
        provider_factory=factory,
        registry=registry,
        metrics_service=metrics,
        startup_time=startup_time,
        app_version=app_version,
    )

    health_status = await service.get_health_status(endpoint="health")
    assert health_status["status"] == "ok"
    assert health_status["application_version"] == "1.2.3"
    assert health_status["application_state"] == "healthy"
    assert health_status["request_count"] == 0
    assert "overall_status" in health_status
    assert "provider_health" in health_status


@pytest.mark.asyncio
async def test_health_endpoints_detailed(get_client) -> None:
    async with get_client() as client:
        for endpoint, status_val in [("/v1/health", "ok"), ("/v1/ready", "ready"), ("/v1/live", "alive")]:
            response = await client.get(endpoint)
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == status_val
            assert "overall_status" in data
            assert "application_version" in data
            assert "uptime" in data
            assert "startup_timestamp" in data
            assert "registered_providers" in data
            assert "registered_models" in data
            assert "provider_health" in data
            assert data["application_state"] == "healthy"
            assert "request_count" in data
            assert "memory_usage" in data


@pytest.mark.asyncio
async def test_request_id_generation_and_headers(get_client) -> None:
    async with get_client() as client:
        # Test generated Request ID
        response = await client.get("/v1/health")
        assert response.status_code == 200
        assert "X-Request-ID" in response.headers
        req_id_1 = response.headers["X-Request-ID"]
        assert len(req_id_1) > 0
    
        # Test custom Request ID
        custom_id = "test-req-id-12345"
        response2 = await client.get("/v1/health", headers={"x-request-id": custom_id})
        assert response2.status_code == 200
        assert response2.headers["X-Request-ID"] == custom_id


@pytest.mark.anyio
async def test_exception_handlers_direct() -> None:
    from starlette.requests import Request
    from starlette.datastructures import Headers

    scope = {"type": "http", "headers": Headers().raw}
    req = Request(scope)

    # 1. ModelNotFoundException
    exc1 = ModelNotFoundException("Model not found test")
    resp1 = await AppExceptionHandler.handle(req, exc1)
    assert resp1.status_code == 404
    data1 = json.loads(resp1.body.decode())
    assert data1["error"]["code"] == "model_not_found"
    assert data1["error"]["message"] == "Model not found test"

    # 2. ProviderNotFoundException
    exc2 = ProviderNotFoundException("Provider not found test")
    resp2 = await AppExceptionHandler.handle(req, exc2)
    assert resp2.status_code == 404
    data2 = json.loads(resp2.body.decode())
    assert data2["error"]["code"] == "provider_not_found"

    # 3. RoutingException
    exc3 = RoutingException("Routing failed test")
    resp3 = await AppExceptionHandler.handle(req, exc3)
    assert resp3.status_code == 500
    data3 = json.loads(resp3.body.decode())
    assert data3["error"]["code"] == "routing_failed"

    # 4. InferenceException
    exc4 = InferenceException("Inference failed test")
    resp4 = await AppExceptionHandler.handle(req, exc4)
    assert resp4.status_code == 500
    data4 = json.loads(resp4.body.decode())
    assert data4["error"]["code"] == "inference_failed"

    # 5. ProviderUnavailableException
    exc5 = ProviderUnavailableException("Provider unavailable test")
    resp5 = await AppExceptionHandler.handle(req, exc5)
    assert resp5.status_code == 502
    data5 = json.loads(resp5.body.decode())
    assert data5["error"]["code"] == "provider_unavailable"

    # 6. ConfigurationException
    exc6 = ConfigurationException("Config failed test")
    resp6 = await AppExceptionHandler.handle(req, exc6)
    assert resp6.status_code == 500
    data6 = json.loads(resp6.body.decode())
    assert data6["error"]["code"] == "configuration_error"

    # 7. ValidationException
    exc7 = ValidationException("Validation failed test")
    resp7 = await AppExceptionHandler.handle(req, exc7)
    assert resp7.status_code == 400
    data7 = json.loads(resp7.body.decode())
    assert data7["error"]["code"] == "validation_error"
