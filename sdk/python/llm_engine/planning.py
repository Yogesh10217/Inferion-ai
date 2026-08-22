"""
Python SDK Client for Autonomous Planning, Reasoning & Self-Improvement Platform
"""

import requests
from typing import Dict, Any, List, Optional


class PlanningClient:
    """Python SDK client for interacting with /v1/plans endpoints."""

    def __init__(self, base_url: str = "http://localhost:8000", api_key: Optional[str] = None):
        self.base_url = base_url.rstrip("/")
        self.headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}

    def create(self, title: str, description: str = "", tenant_id: str = "global") -> Dict[str, Any]:
        url = f"{self.base_url}/v1/plans"
        payload = {"title": title, "description": description, "tenant_id": tenant_id}
        resp = requests.post(url, json=payload, headers=self.headers)
        resp.raise_for_status()
        return resp.json().get("plan", {})

    def list(self, tenant_id: str = "global") -> List[Dict[str, Any]]:
        url = f"{self.base_url}/v1/plans"
        resp = requests.get(url, params={"tenant_id": tenant_id}, headers=self.headers)
        resp.raise_for_status()
        return resp.json().get("plans", [])

    def get(self, plan_id: str) -> Dict[str, Any]:
        url = f"{self.base_url}/v1/plans/{plan_id}"
        resp = requests.get(url, headers=self.headers)
        resp.raise_for_status()
        return resp.json().get("plan", {})

    def update(self, plan_id: str, title: Optional[str] = None, confidence_score: Optional[float] = None) -> Dict[str, Any]:
        url = f"{self.base_url}/v1/plans/{plan_id}"
        params = {}
        if title: params["title"] = title
        if confidence_score is not None: params["confidence_score"] = confidence_score
        resp = requests.patch(url, params=params, headers=self.headers)
        resp.raise_for_status()
        return resp.json()

    def delete(self, plan_id: str) -> Dict[str, Any]:
        url = f"{self.base_url}/v1/plans/{plan_id}"
        resp = requests.delete(url, headers=self.headers)
        resp.raise_for_status()
        return resp.json()

    def simulate(self, plan_id: str) -> Dict[str, Any]:
        url = f"{self.base_url}/v1/plans/{plan_id}/simulate"
        resp = requests.post(url, headers=self.headers)
        resp.raise_for_status()
        return resp.json().get("simulation", {})

    def execute(self, plan_id: str, budget_dollars: float = 50.0) -> Dict[str, Any]:
        url = f"{self.base_url}/v1/plans/{plan_id}/execute"
        payload = {"budget_dollars": budget_dollars}
        resp = requests.post(url, json=payload, headers=self.headers)
        resp.raise_for_status()
        return resp.json()

    def reflect(self, plan_id: str) -> Dict[str, Any]:
        url = f"{self.base_url}/v1/plans/{plan_id}/reflect"
        resp = requests.post(url, headers=self.headers)
        resp.raise_for_status()
        return resp.json().get("reflection", {})

    def optimize(self, plan_id: str) -> Dict[str, Any]:
        url = f"{self.base_url}/v1/plans/{plan_id}/optimize"
        resp = requests.post(url, headers=self.headers)
        resp.raise_for_status()
        return resp.json().get("plan", {})

    def metrics(self, plan_id: str) -> Dict[str, Any]:
        url = f"{self.base_url}/v1/plans/{plan_id}/metrics"
        resp = requests.get(url, headers=self.headers)
        resp.raise_for_status()
        return resp.json().get("metrics", {})

    def billing(self, plan_id: str) -> Dict[str, Any]:
        url = f"{self.base_url}/v1/plans/{plan_id}/billing"
        resp = requests.get(url, headers=self.headers)
        resp.raise_for_status()
        return resp.json().get("billing", {})

    def history(self, plan_id: str) -> List[Dict[str, Any]]:
        url = f"{self.base_url}/v1/plans/{plan_id}/history"
        resp = requests.get(url, headers=self.headers)
        resp.raise_for_status()
        return resp.json().get("history", [])
