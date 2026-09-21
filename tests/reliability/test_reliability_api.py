"""Integration tests for Phase 5.9 REST API Routers."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_security_api_keys_flow():
    # Create key
    res_create = client.post("/v1/security/api-keys", json={"name": "integration-key", "tenant_id": "t_int"})
    assert res_create.status_code == 201
    data = res_create.json()["api_key"]
    key_id = data["key_id"]

    # List keys
    res_list = client.get("/v1/security/api-keys?tenant_id=t_int")
    assert res_list.status_code == 200
    assert len(res_list.json()["api_keys"]) >= 1

    # Revoke key
    res_revoke = client.delete(f"/v1/security/api-keys/{key_id}")
    assert res_revoke.status_code == 200


def test_governance_api_flow():
    res_usage = client.get("/v1/governance/usage?tenant_id=global")
    assert res_usage.status_code == 200
    assert "usage" in res_usage.json()

    res_quotas = client.get("/v1/governance/quotas?tenant_id=global")
    assert res_quotas.status_code == 200
    assert "remaining" in res_quotas.json()


def test_jobs_api_flow():
    res_enqueue = client.post("/v1/jobs", json={"name": "api_job", "handler_name": "sample"})
    assert res_enqueue.status_code == 201
    job_id = res_enqueue.json()["job"]["job_id"]

    res_get = client.get(f"/v1/jobs/{job_id}")
    assert res_get.status_code == 200

    res_cancel = client.post(f"/v1/jobs/{job_id}/cancel")
    assert res_cancel.status_code == 200


def test_reliability_api_flow():
    res_health = client.get("/v1/reliability/health")
    assert res_health.status_code == 200
    assert res_health.json()["status"] == "HEALTHY"

    res_breakers = client.get("/v1/reliability/circuit-breakers")
    assert res_breakers.status_code == 200
