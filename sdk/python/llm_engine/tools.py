"""
Python SDK Client for Enterprise Tool Calling & MCP Platform
"""

import requests
from typing import Dict, Any, List, Optional


class ToolsClient:
    """Python SDK client for interacting with /v1/tools endpoints."""

    def __init__(self, base_url: str = "http://localhost:8000", api_key: Optional[str] = None):
        self.base_url = base_url.rstrip("/")
        self.headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}

    def create(self, name: str, description: str, category: str = "custom", parameters_schema: Optional[Dict[str, Any]] = None, cost_estimate: float = 0.0) -> Dict[str, Any]:
        url = f"{self.base_url}/v1/tools"
        payload = {
            "name": name,
            "description": description,
            "category": category,
            "parameters_schema": parameters_schema or {},
            "cost_estimate": cost_estimate,
        }
        resp = requests.post(url, json=payload, headers=self.headers)
        resp.raise_for_status()
        return resp.json()

    def list(self, category: Optional[str] = None, tenant_id: str = "global") -> List[Dict[str, Any]]:
        url = f"{self.base_url}/v1/tools"
        params = {"tenant_id": tenant_id}
        if category:
            params["category"] = category
        resp = requests.get(url, params=params, headers=self.headers)
        resp.raise_for_status()
        return resp.json().get("tools", [])

    def get(self, tool_id: str, tenant_id: str = "global") -> Dict[str, Any]:
        url = f"{self.base_url}/v1/tools/{tool_id}"
        resp = requests.get(url, params={"tenant_id": tenant_id}, headers=self.headers)
        resp.raise_for_status()
        return resp.json().get("tool", {})

    def delete(self, tool_id: str, tenant_id: str = "global") -> Dict[str, Any]:
        url = f"{self.base_url}/v1/tools/{tool_id}"
        resp = requests.delete(url, params={"tenant_id": tenant_id}, headers=self.headers)
        resp.raise_for_status()
        return resp.json()

    def execute(self, tool_id: str, parameters: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = f"{self.base_url}/v1/tools/{tool_id}/execute"
        payload = {"parameters": parameters, "context": context}
        resp = requests.post(url, json=payload, headers=self.headers)
        resp.raise_for_status()
        return resp.json().get("result", {})

    def validate(self, tool_id: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.base_url}/v1/tools/{tool_id}/validate"
        payload = {"parameters": parameters}
        resp = requests.post(url, json=payload, headers=self.headers)
        resp.raise_for_status()
        return resp.json()

    def audit(self, tool_id: str, tenant_id: str = "global") -> Dict[str, Any]:
        url = f"{self.base_url}/v1/tools/{tool_id}/audit"
        resp = requests.get(url, params={"tenant_id": tenant_id}, headers=self.headers)
        resp.raise_for_status()
        return resp.json()

    def metrics(self, tool_id: str, tenant_id: str = "global") -> Dict[str, Any]:
        url = f"{self.base_url}/v1/tools/{tool_id}/metrics"
        resp = requests.get(url, params={"tenant_id": tenant_id}, headers=self.headers)
        resp.raise_for_status()
        return resp.json()
