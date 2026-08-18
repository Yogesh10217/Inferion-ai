"""
Python SDK Client for Enterprise Multi-Agent Collaboration Platform
"""

import requests
from typing import Dict, Any, List, Optional


class TeamsClient:
    """Python SDK client for interacting with /v1/teams endpoints."""

    def __init__(self, base_url: str = "http://localhost:8000", api_key: Optional[str] = None):
        self.base_url = base_url.rstrip("/")
        self.headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}

    def create(self, name: str, team_type: str = "custom", description: str = "", budget_dollars: float = 10.0) -> Dict[str, Any]:
        url = f"{self.base_url}/v1/teams"
        payload = {"name": name, "team_type": team_type, "description": description, "budget_dollars": budget_dollars}
        resp = requests.post(url, json=payload, headers=self.headers)
        resp.raise_for_status()
        return resp.json()

    def list(self, tenant_id: str = "global") -> List[Dict[str, Any]]:
        url = f"{self.base_url}/v1/teams"
        resp = requests.get(url, params={"tenant_id": tenant_id}, headers=self.headers)
        resp.raise_for_status()
        return resp.json().get("teams", [])

    def get(self, team_id: str) -> Dict[str, Any]:
        url = f"{self.base_url}/v1/teams/{team_id}"
        resp = requests.get(url, headers=self.headers)
        resp.raise_for_status()
        return resp.json()

    def update(self, team_id: str, description: Optional[str] = None, budget_dollars: Optional[float] = None) -> Dict[str, Any]:
        url = f"{self.base_url}/v1/teams/{team_id}"
        params = {}
        if description: params["description"] = description
        if budget_dollars is not None: params["budget_dollars"] = budget_dollars
        resp = requests.patch(url, params=params, headers=self.headers)
        resp.raise_for_status()
        return resp.json()

    def delete(self, team_id: str) -> Dict[str, Any]:
        url = f"{self.base_url}/v1/teams/{team_id}"
        resp = requests.delete(url, headers=self.headers)
        resp.raise_for_status()
        return resp.json()

    def run(self, team_id: str, goal: str, inputs: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = f"{self.base_url}/v1/teams/{team_id}/run"
        payload = {"goal": goal, "inputs": inputs or {}}
        resp = requests.post(url, json=payload, headers=self.headers)
        resp.raise_for_status()
        return resp.json().get("result", {})

    def pause(self, team_id: str) -> Dict[str, Any]:
        url = f"{self.base_url}/v1/teams/{team_id}/pause"
        resp = requests.post(url, headers=self.headers)
        resp.raise_for_status()
        return resp.json()

    def resume(self, team_id: str) -> Dict[str, Any]:
        url = f"{self.base_url}/v1/teams/{team_id}/resume"
        resp = requests.post(url, headers=self.headers)
        resp.raise_for_status()
        return resp.json()

    def cancel(self, team_id: str) -> Dict[str, Any]:
        url = f"{self.base_url}/v1/teams/{team_id}/cancel"
        resp = requests.post(url, headers=self.headers)
        resp.raise_for_status()
        return resp.json()

    def members(self, team_id: str) -> List[Dict[str, Any]]:
        url = f"{self.base_url}/v1/teams/{team_id}/members"
        resp = requests.get(url, headers=self.headers)
        resp.raise_for_status()
        return resp.json().get("members", [])

    def add_member(self, team_id: str, name: str, role: str = "executor", system_prompt: str = "") -> Dict[str, Any]:
        url = f"{self.base_url}/v1/teams/{team_id}/members"
        payload = {"name": name, "role": role, "system_prompt": system_prompt}
        resp = requests.post(url, json=payload, headers=self.headers)
        resp.raise_for_status()
        return resp.json().get("member", {})

    def messages(self, team_id: str) -> List[Dict[str, Any]]:
        url = f"{self.base_url}/v1/teams/{team_id}/messages"
        resp = requests.get(url, headers=self.headers)
        resp.raise_for_status()
        return resp.json().get("messages", [])

    def history(self, team_id: str) -> List[Dict[str, Any]]:
        url = f"{self.base_url}/v1/teams/{team_id}/history"
        resp = requests.get(url, headers=self.headers)
        resp.raise_for_status()
        return resp.json().get("history", [])

    def metrics(self, team_id: str) -> Dict[str, Any]:
        url = f"{self.base_url}/v1/teams/{team_id}/metrics"
        resp = requests.get(url, headers=self.headers)
        resp.raise_for_status()
        return resp.json().get("metrics", {})

    def billing(self, team_id: str) -> Dict[str, Any]:
        url = f"{self.base_url}/v1/teams/{team_id}/billing"
        resp = requests.get(url, headers=self.headers)
        resp.raise_for_status()
        return resp.json().get("billing", {})
