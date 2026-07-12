from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoint() -> None:
    response = client.get("/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_ready_and_live_endpoints() -> None:
    ready = client.get("/v1/ready")
    live = client.get("/v1/live")
    assert ready.status_code == 200
    assert live.status_code == 200
    assert ready.json()["status"] == "ready"
    assert live.json()["status"] == "alive"
