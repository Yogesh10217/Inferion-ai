"""
Workflows SDK Client Subsystem
"""

from typing import Dict, Any, List, Optional
import httpx


class WorkflowClient:
    """Python SDK Client for Enterprise Workflow Engine."""

    def __init__(self, client: httpx.Client, base_url: str):
        self._client = client
        self.base_url = base_url

    def create(
        self,
        name: str,
        description: str = "",
        spec: Optional[Dict[str, Any]] = None,
        workflow_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        payload = {"name": name, "description": description, "spec": spec, "id": workflow_id}
        resp = self._client.post(f"{self.base_url}/v1/workflows", json=payload)
        resp.raise_for_status()
        return resp.json()

    def list(self) -> List[Dict[str, Any]]:
        resp = self._client.get(f"{self.base_url}/v1/workflows")
        resp.raise_for_status()
        return resp.json()

    def get(self, workflow_id: str) -> Dict[str, Any]:
        resp = self._client.get(f"{self.base_url}/v1/workflows/{workflow_id}")
        resp.raise_for_status()
        return resp.json()

    def run(self, workflow_id: str, inputs: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        payload = {"inputs": inputs or {}}
        resp = self._client.post(f"{self.base_url}/v1/workflows/{workflow_id}/run", json=payload)
        resp.raise_for_status()
        return resp.json()

    def resume(self, run_id: str, approved: Optional[bool] = None, feedback: Optional[str] = None) -> Dict[str, Any]:
        payload = {}
        if approved is not None:
            payload["approved"] = approved
        if feedback:
            payload["feedback"] = feedback
        resp = self._client.post(f"{self.base_url}/v1/workflows/{run_id}/resume", json=payload)
        resp.raise_for_status()
        return resp.json()

    def approve(self, run_id: str, approved: bool = True, feedback: Optional[str] = None) -> Dict[str, Any]:
        payload = {"approved": approved, "feedback": feedback}
        resp = self._client.post(f"{self.base_url}/v1/workflows/{run_id}/approve", json=payload)
        resp.raise_for_status()
        return resp.json()

    def history(self, run_id: str) -> Dict[str, Any]:
        resp = self._client.get(f"{self.base_url}/v1/workflows/{run_id}/history")
        resp.raise_for_status()
        return resp.json()

    def checkpoints(self, run_id: str) -> List[Dict[str, Any]]:
        resp = self._client.get(f"{self.base_url}/v1/workflows/{run_id}/checkpoints")
        resp.raise_for_status()
        return resp.json()

    def rollback(self, run_id: str, checkpoint_id: Optional[str] = None) -> Dict[str, Any]:
        payload = {"checkpoint_id": checkpoint_id}
        resp = self._client.post(f"{self.base_url}/v1/workflows/{run_id}/rollback", json=payload)
        resp.raise_for_status()
        return resp.json()

    def fork(self, run_id: str, checkpoint_id: Optional[str] = None) -> Dict[str, Any]:
        payload = {"checkpoint_id": checkpoint_id}
        resp = self._client.post(f"{self.base_url}/v1/workflows/{run_id}/fork", json=payload)
        resp.raise_for_status()
        return resp.json()
