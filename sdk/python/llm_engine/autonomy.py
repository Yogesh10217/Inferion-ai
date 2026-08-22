"""
Python SDK Client for Autonomous Execution & Digital Workforce Platform
"""

import requests
from typing import Dict, Any, List, Optional


class AutonomyClient:
    """Python SDK client for /v1/autonomy endpoints."""

    def __init__(self, base_url: str = "http://localhost:8000", api_key: Optional[str] = None):
        self.base_url = base_url.rstrip("/")
        self.headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}

    def submit_goal(self, goal: str, tenant_id: str = "global") -> Dict[str, Any]:
        url = f"{self.base_url}/v1/autonomy/goals"
        payload = {"goal": goal, "tenant_id": tenant_id}
        resp = requests.post(url, json=payload, headers=self.headers)
        resp.raise_for_status()
        return resp.json().get("execution", {})

    def pause(self, execution_id: str) -> Dict[str, Any]:
        url = f"{self.base_url}/v1/autonomy/pause"
        resp = requests.post(url, params={"execution_id": execution_id}, headers=self.headers)
        resp.raise_for_status()
        return resp.json()

    def resume(self, execution_id: str) -> Dict[str, Any]:
        url = f"{self.base_url}/v1/autonomy/resume"
        resp = requests.post(url, params={"execution_id": execution_id}, headers=self.headers)
        resp.raise_for_status()
        return resp.json()

    def stop(self, execution_id: str) -> Dict[str, Any]:
        url = f"{self.base_url}/v1/autonomy/stop"
        resp = requests.post(url, params={"execution_id": execution_id}, headers=self.headers)
        resp.raise_for_status()
        return resp.json()

    def list_executions(self) -> List[Dict[str, Any]]:
        url = f"{self.base_url}/v1/autonomy/executions"
        resp = requests.get(url, headers=self.headers)
        resp.raise_for_status()
        return resp.json().get("executions", [])

    def get_execution(self, execution_id: str) -> Dict[str, Any]:
        url = f"{self.base_url}/v1/autonomy/executions/{execution_id}"
        resp = requests.get(url, headers=self.headers)
        resp.raise_for_status()
        return resp.json()


class WorkersClient:
    """Python SDK client for /v1/workers endpoints."""

    def __init__(self, base_url: str = "http://localhost:8000", api_key: Optional[str] = None):
        self.base_url = base_url.rstrip("/")
        self.headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}

    def create(self, name: str, template_type: str = "custom", tenant_id: str = "global") -> Dict[str, Any]:
        url = f"{self.base_url}/v1/workers"
        payload = {"name": name, "template_type": template_type, "tenant_id": tenant_id}
        resp = requests.post(url, json=payload, headers=self.headers)
        resp.raise_for_status()
        return resp.json().get("worker", {})

    def list(self, tenant_id: str = "global") -> List[Dict[str, Any]]:
        url = f"{self.base_url}/v1/workers"
        resp = requests.get(url, params={"tenant_id": tenant_id}, headers=self.headers)
        resp.raise_for_status()
        return resp.json().get("workers", [])

    def get(self, worker_id: str) -> Dict[str, Any]:
        url = f"{self.base_url}/v1/workers/{worker_id}"
        resp = requests.get(url, headers=self.headers)
        resp.raise_for_status()
        return resp.json().get("worker", {})

    def terminate(self, worker_id: str) -> Dict[str, Any]:
        url = f"{self.base_url}/v1/workers/{worker_id}"
        resp = requests.delete(url, headers=self.headers)
        resp.raise_for_status()
        return resp.json()

    def assign_goal(self, worker_id: str, goal: str) -> Dict[str, Any]:
        url = f"{self.base_url}/v1/workers/{worker_id}/goal"
        payload = {"goal": goal}
        resp = requests.post(url, json=payload, headers=self.headers)
        resp.raise_for_status()
        return resp.json().get("result", {})
