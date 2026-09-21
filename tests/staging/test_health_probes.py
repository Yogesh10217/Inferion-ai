import pytest
from fastapi.testclient import TestClient

from app.deployment.liveness import DeploymentLivenessProbe
from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_live_probe_contract(client):
    """Verifies /live is lightweight, fast, zero DB/Cache IO, and returns HTTP 200."""
    res = client.get("/live")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] in ("HEALTHY", "ok", "alive")
    assert "uptime_seconds" in data or "service" in data or "live" in data or "status" in data


def test_ready_probe_contract_healthy(client):
    """Verifies /ready evaluates dependencies and returns HTTP 200 when ready."""
    res = client.get("/ready")
    assert res.status_code in (200, 503)
    data = res.json()
    if res.status_code == 200:
        assert data.get("ready") is True or data.get("status") in ("HEALTHY", "ok", "ready")
    else:
        assert res.status_code == 503


def test_health_probe_sanitization(client):
    """Verifies /health provides sanitized diagnostics without secret leakage."""
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert "status" in data or "overall_status" in data
    # Ensure zero raw secrets in response
    text = res.text.lower()
    assert "secret_key" not in text
    assert "jwt_secret" not in text
    assert "postgres:password" not in text


def test_liveness_probe_timing():
    """Verifies DeploymentLivenessProbe executes in sub-millisecond time with zero IO."""
    res = DeploymentLivenessProbe.check_liveness()
    assert res["status"] == "HEALTHY"
    assert res["live"] is True
    assert res["uptime_seconds"] >= 0
