"""Integration tests for Governance Platform REST API endpoints."""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_governance_rest_api_lifecycle():
    # 1. Health
    res_h = client.get("/v1/governance/health")
    assert res_h.status_code == 200

    # 2. Evaluate Policy
    res_pol = client.post("/v1/governance/policies/evaluate", json={
        "action": "read",
        "resource_id": "dataset_1",
        "tenant_id": "t_api_gov",
        "actor_id": "user_1",
    })
    assert res_pol.status_code == 200
    assert res_pol.json()["decision"] == "ALLOW"

    # 3. Assess Risk
    res_risk = client.post("/v1/governance/risk/assess", json={
        "target_resource_id": "agent_x",
        "category": "SECURITY",
        "factors": [{"name": "Public Access", "weight": 1.0, "impact_score": 20.0}],
        "tenant_id": "t_api_gov",
    })
    assert res_risk.status_code == 201
    assert res_risk.json()["overall_score"] == 20.0

    # 4. Assess Compliance
    res_comp = client.post("/v1/governance/compliance/assess", json={
        "framework": "SOC2",
        "tenant_id": "t_api_gov",
    })
    assert res_comp.status_code == 201

    # 5. Record Violation
    res_viol = client.post("/v1/governance/violations", json={
        "title": "Unapproved Access",
        "violation_type": "ACCESS_VIOLATION",
        "severity": "MEDIUM",
        "primary_resource_id": "res_y",
        "tenant_id": "t_api_gov",
    })
    assert res_viol.status_code == 201

    # 6. Audit Package Report
    res_rep = client.get("/v1/governance/reports/audit-package", params={"tenant_id": "t_api_gov"})
    assert res_rep.status_code == 200
