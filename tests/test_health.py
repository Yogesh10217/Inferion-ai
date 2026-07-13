from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoint() -> None:
    response = client.get("/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
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


def test_ready_and_live_endpoints() -> None:
    ready = client.get("/v1/ready")
    live = client.get("/v1/live")
    assert ready.status_code == 200
    assert live.status_code == 200
    assert ready.json()["status"] == "ready"
    assert live.json()["status"] == "alive"
