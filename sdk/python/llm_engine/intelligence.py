"""Python SDK Client for Enterprise AI Intelligence Platform."""

from typing import Dict, Any, List, Optional


class IntelligenceClient:
    """Client interface for interacting with Intelligence Platform REST API."""

    def __init__(self, client: Any) -> None:
        self.client = client

    def ingest_signal(self, source: str, signal_type: str, message: str, tenant_id: str = "global", resource_id: Optional[str] = None) -> Dict[str, Any]:
        payload = {
            "source": source,
            "signal_type": signal_type,
            "message": message,
            "tenant_id": tenant_id,
            "resource_id": resource_id,
        }
        return self.client.post("/v1/intelligence/signals", json=payload)

    def analyze(self, tenant_id: str = "global", resource_id: str = "res_1") -> Dict[str, Any]:
        return self.client.post(f"/v1/intelligence/analyze?tenant_id={tenant_id}&resource_id={resource_id}")

    def forecast(self, target_resource_id: str, forecast_type: str = "INCIDENT_RISK_FORECAST", tenant_id: str = "global") -> Dict[str, Any]:
        payload = {"target_resource_id": target_resource_id, "forecast_type": forecast_type, "tenant_id": tenant_id}
        return self.client.post("/v1/intelligence/forecast", json=payload)

    def simulate(self, target_resource_id: str, action_type: str = "ROLLBACK", tenant_id: str = "global") -> Dict[str, Any]:
        payload = {"target_resource_id": target_resource_id, "action_type": action_type, "tenant_id": tenant_id}
        return self.client.post("/v1/intelligence/simulate", json=payload)

    def optimize(self, objective: str, candidates: List[Dict[str, Any]], tenant_id: str = "global") -> Dict[str, Any]:
        payload = {"objective": objective, "candidates": candidates, "tenant_id": tenant_id}
        return self.client.post("/v1/intelligence/optimize", json=payload)

    def recommend(self, recommendation_type: str, title: str, action_description: str, target_resource_id: str, tenant_id: str = "global", risk_level: str = "LOW") -> Dict[str, Any]:
        payload = {
            "recommendation_type": recommendation_type,
            "title": title,
            "action_description": action_description,
            "target_resource_id": target_resource_id,
            "tenant_id": tenant_id,
            "risk_level": risk_level,
        }
        return self.client.post("/v1/intelligence/recommend", json=payload)

    def create_decision(self, title: str, tenant_id: str = "global") -> Dict[str, Any]:
        return self.client.post(f"/v1/intelligence/decisions?tenant_id={tenant_id}&title={title}")

    def approve_decision(self, decision_id: str, tenant_id: str = "global") -> Dict[str, Any]:
        payload = {"reviewer_user_id": "admin", "tenant_id": tenant_id}
        return self.client.post(f"/v1/intelligence/decisions/{decision_id}/approve", json=payload)

    def execute_decision(self, decision_id: str, target: str = "PLATFORM_OPERATIONS", tenant_id: str = "global") -> Dict[str, Any]:
        payload = {"target": target, "tenant_id": tenant_id}
        return self.client.post(f"/v1/intelligence/decisions/{decision_id}/execute", json=payload)

    def list_insights(self, tenant_id: str = "global") -> List[Dict[str, Any]]:
        return self.client.get(f"/v1/intelligence/insights?tenant_id={tenant_id}")

    def list_recommendations(self, tenant_id: str = "global") -> List[Dict[str, Any]]:
        return self.client.get(f"/v1/intelligence/recommendations?tenant_id={tenant_id}")

    def get_analytics(self, tenant_id: str = "global") -> Dict[str, Any]:
        return self.client.get(f"/v1/intelligence/analytics?tenant_id={tenant_id}")
