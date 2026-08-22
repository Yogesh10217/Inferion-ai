"""Integration tests for FinOps REST API endpoints."""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_finops_rest_api_lifecycle():
    # 1. Create budget
    res_b = client.post("/v1/finops/budgets", json={
        "name": "API FinOps Budget",
        "limit_amount": "500.0",
        "tenant_id": "t_api_fin",
        "enforcement_action": "WARN",
    })
    assert res_b.status_code == 201
    budget_id = res_b.json()["budget"]["budget_id"]

    # 2. List budgets
    res_bl = client.get("/v1/finops/budgets", params={"tenant_id": "t_api_fin"})
    assert res_bl.status_code == 200
    assert len(res_bl.json()["budgets"]) == 1

    # 3. Evaluate budget
    res_ev = client.post("/v1/finops/budgets/evaluate", json={
        "tenant_id": "t_api_fin",
        "projected_cost": "10.0",
    })
    assert res_ev.status_code == 200
    assert res_ev.json()["decision"]["permitted"] is True

    # 4. Get costs
    res_c = client.get("/v1/finops/costs", params={"tenant_id": "t_api_fin"})
    assert res_c.status_code == 200

    # 5. Get showback report
    res_sb = client.get("/v1/finops/showback", params={"tenant_id": "t_api_fin"})
    assert res_sb.status_code == 200
