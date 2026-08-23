"""Data Governance Python SDK Client."""

import httpx
from typing import Dict, Any, List, Optional


class DataGovernanceClient:
    """Client for interacting with Enterprise AI Data Governance Platform."""

    def __init__(self, client: httpx.Client) -> None:
        self.client = client

    def list_assets(self, tenant_id: str = "global") -> Dict[str, Any]:
        resp = self.client.get(f"/v1/data-governance/assets?tenant_id={tenant_id}")
        resp.raise_for_status()
        return resp.json()

    def get_asset(self, asset_id: str, tenant_id: str = "global") -> Dict[str, Any]:
        resp = self.client.get(f"/v1/data-governance/assets/{asset_id}?tenant_id={tenant_id}")
        resp.raise_for_status()
        return resp.json()

    def create_asset(self, name: str, tenant_id: str = "global", asset_type: str = "DATASET", owner_id: str = "system") -> Dict[str, Any]:
        resp = self.client.post("/v1/data-governance/assets", json={
            "tenant_id": tenant_id,
            "name": name,
            "asset_type": asset_type,
            "owner_id": owner_id,
        })
        resp.raise_for_status()
        return resp.json()

    def classify_asset(self, asset_id: str, tenant_id: str = "global", content_sample: Optional[str] = None) -> Dict[str, Any]:
        resp = self.client.post(f"/v1/data-governance/assets/{asset_id}/classify", json={
            "tenant_id": tenant_id,
            "content_sample": content_sample,
        })
        resp.raise_for_status()
        return resp.json()

    def evaluate_access(self, principal_id: str, asset_id: str, tenant_id: str = "global", action: str = "READ") -> Dict[str, Any]:
        resp = self.client.post("/v1/data-governance/access/evaluate", json={
            "tenant_id": tenant_id,
            "principal_id": principal_id,
            "asset_id": asset_id,
            "action": action,
        })
        resp.raise_for_status()
        return resp.json()

    def get_trust_score(self, asset_id: str, tenant_id: str = "global") -> Dict[str, Any]:
        resp = self.client.get(f"/v1/data-governance/trust/{asset_id}?tenant_id={tenant_id}")
        resp.raise_for_status()
        return resp.json()

    def get_analytics(self, tenant_id: str = "global") -> Dict[str, Any]:
        resp = self.client.get(f"/v1/data-governance/analytics?tenant_id={tenant_id}")
        resp.raise_for_status()
        return resp.json()
