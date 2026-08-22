"""Integration tests for Identity REST API endpoints."""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_identity_rest_api_lifecycle():
    # 1. Health
    res_h = client.get("/v1/identity/health")
    assert res_h.status_code == 200

    # 2. Create Identity
    res_id = client.post("/v1/identity/identities", json={
        "username": "api_user",
        "identity_type": "HUMAN",
        "tenant_id": "t_api_id",
        "roles": ["developer"],
    })
    assert res_id.status_code == 201
    ident_id = res_id.json()["identity_id"]

    # 3. Authenticate
    res_auth = client.post("/v1/identity/authenticate", json={
        "identity_id": ident_id,
        "method": "JWT",
        "tenant_id": "t_api_id",
    })
    assert res_auth.status_code == 200
    assert res_auth.json()["is_authenticated"] is True

    # 4. Request JIT Privileged Access
    res_jit = client.post("/v1/identity/privileged-access/request", json={
        "identity_id": ident_id,
        "role": "TENANT_ADMIN",
        "tenant_id": "t_api_id",
        "duration_minutes": 30,
    })
    assert res_jit.status_code == 201

    # 5. Zero Trust Evaluate
    res_zt = client.post("/v1/identity/zero-trust/evaluate", json={
        "identity_id": ident_id,
        "tenant_id": "t_api_id",
        "network_trusted": True,
        "device_trusted": True,
        "risk_score": 10.0,
    })
    assert res_zt.status_code == 200
    assert res_zt.json()["trust_level"] == "TRUSTED"
