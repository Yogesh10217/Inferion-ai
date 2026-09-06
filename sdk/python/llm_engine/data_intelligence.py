"""Python SDK Client for Data Intelligence Platform (Phase 5.43)."""

from typing import Dict, Any, List, Optional
import httpx


class DataIntelligenceClient:
    """Python SDK client for Data Intelligence, Quality, Lineage, Anomalies, Drift, and Trust."""

    def __init__(self, base_url: str = "http://localhost:8000", api_key: Optional[str] = None, timeout: float = 30.0) -> None:
        self.base_url = base_url.rstrip("/")
        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        self.client = httpx.Client(base_url=self.base_url, headers=headers, timeout=timeout)

    def register_dataset(self, name: str, tenant_id: str = "global", dataset_type: str = "TABLE", source_id: Optional[str] = None) -> Dict[str, Any]:
        resp = self.client.post("/v1/data/datasets", json={"name": name, "tenant_id": tenant_id, "dataset_type": dataset_type, "source_id": source_id})
        resp.raise_for_status()
        return resp.json()

    def list_datasets(self, tenant_id: str = "global") -> List[Dict[str, Any]]:
        resp = self.client.get(f"/v1/data/datasets?tenant_id={tenant_id}")
        resp.raise_for_status()
        return resp.json()

    def evaluate_quality(self, dataset_id: str, tenant_id: str = "global") -> Dict[str, Any]:
        resp = self.client.post("/v1/data/quality/evaluate", json={"dataset_id": dataset_id, "tenant_id": tenant_id})
        resp.raise_for_status()
        return resp.json()

    def detect_anomaly(self, dataset_id: str, metric_name: str, expected_value: float, actual_value: float, tenant_id: str = "global") -> Dict[str, Any]:
        resp = self.client.post("/v1/data/anomalies", json={
            "dataset_id": dataset_id,
            "tenant_id": tenant_id,
            "metric_name": metric_name,
            "expected_value": expected_value,
            "actual_value": actual_value,
        })
        resp.raise_for_status()
        return resp.json()

    def list_anomalies(self, tenant_id: str = "global") -> List[Dict[str, Any]]:
        resp = self.client.get(f"/v1/data/anomalies?tenant_id={tenant_id}")
        resp.raise_for_status()
        return resp.json()

    def get_trust(self, dataset_id: str, tenant_id: str = "global") -> Dict[str, Any]:
        resp = self.client.get(f"/v1/data/trust?dataset_id={dataset_id}&tenant_id={tenant_id}")
        resp.raise_for_status()
        return resp.json()

    def get_analytics(self, tenant_id: str = "global") -> Dict[str, Any]:
        resp = self.client.get(f"/v1/data/analytics?tenant_id={tenant_id}")
        resp.raise_for_status()
        return resp.json()
