"""Python SDK Client for FinOps API."""

from typing import Dict, Any, List, Optional
import httpx


class FinOpsClient:
    """Python SDK client for FinOps Cost Ledger, Budgets, Analytics, Forecasting, and Optimization."""

    def __init__(self, base_url: str = "http://localhost:8000", api_key: Optional[str] = None, timeout: float = 30.0) -> None:
        self.base_url = base_url.rstrip("/")
        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        self.client = httpx.Client(base_url=self.base_url, headers=headers, timeout=timeout)

    def list_costs(self, tenant_id: Optional[str] = None) -> Dict[str, Any]:
        params = {"tenant_id": tenant_id} if tenant_id else {}
        resp = self.client.get("/v1/finops/costs", params=params)
        resp.raise_for_status()
        return resp.json()

    def create_budget(self, name: str, limit_amount: str, tenant_id: str = "global", enforcement_action: str = "WARN") -> Dict[str, Any]:
        resp = self.client.post("/v1/finops/budgets", json={"name": name, "limit_amount": limit_amount, "tenant_id": tenant_id, "enforcement_action": enforcement_action})
        resp.raise_for_status()
        return resp.json()

    def list_budgets(self, tenant_id: Optional[str] = None) -> Dict[str, Any]:
        params = {"tenant_id": tenant_id} if tenant_id else {}
        resp = self.client.get("/v1/finops/budgets", params=params)
        resp.raise_for_status()
        return resp.json()

    def get_forecast(self, tenant_id: str = "global") -> Dict[str, Any]:
        resp = self.client.post("/v1/finops/forecasts", params={"tenant_id": tenant_id})
        resp.raise_for_status()
        return resp.json()
