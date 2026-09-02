"""Python SDK Client for FinOps Intelligence Platform (Phase 5.42)."""

from typing import Dict, Any, List, Optional
import httpx


class FinOpsClient:
    """Python SDK client for FinOps Intelligence, Cost Intelligence, Budgets, and Optimization."""

    def __init__(self, base_url: str = "http://localhost:8000", api_key: Optional[str] = None, timeout: float = 30.0) -> None:
        self.base_url = base_url.rstrip("/")
        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        self.client = httpx.Client(base_url=self.base_url, headers=headers, timeout=timeout)

    def record_cost(self, tenant_id: str, category: str, amount_usd: float) -> Dict[str, Any]:
        resp = self.client.post("/v1/finops/costs", json={
            "tenant_id": tenant_id,
            "category": category,
            "amount_usd": amount_usd,
        })
        resp.raise_for_status()
        return resp.json()

    def list_costs(self, tenant_id: str = "global") -> List[Dict[str, Any]]:
        resp = self.client.get(f"/v1/finops/costs?tenant_id={tenant_id}")
        resp.raise_for_status()
        return resp.json()

    def create_budget(self, tenant_id: str, name: str, amount_usd: float, warning_threshold_pct: float = 75.0, critical_threshold_pct: float = 90.0) -> Dict[str, Any]:
        resp = self.client.post("/v1/finops/budgets", json={
            "tenant_id": tenant_id,
            "name": name,
            "amount_usd": amount_usd,
            "warning_threshold_pct": warning_threshold_pct,
            "critical_threshold_pct": critical_threshold_pct,
        })
        resp.raise_for_status()
        return resp.json()

    def list_budgets(self, tenant_id: str = "global") -> List[Dict[str, Any]]:
        resp = self.client.get(f"/v1/finops/budgets?tenant_id={tenant_id}")
        resp.raise_for_status()
        return resp.json()

    def create_optimization(self, tenant_id: str, target_resource_id: str, estimated_monthly_savings_usd: float, action_summary: str, is_high_risk: bool = False) -> Dict[str, Any]:
        resp = self.client.post("/v1/finops/optimization", json={
            "tenant_id": tenant_id,
            "target_resource_id": target_resource_id,
            "estimated_monthly_savings_usd": estimated_monthly_savings_usd,
            "action_summary": action_summary,
            "is_high_risk": is_high_risk,
        })
        resp.raise_for_status()
        return resp.json()

    def get_analytics(self, tenant_id: str = "global") -> Dict[str, Any]:
        resp = self.client.get(f"/v1/finops/analytics?tenant_id={tenant_id}")
        resp.raise_for_status()
        return resp.json()
