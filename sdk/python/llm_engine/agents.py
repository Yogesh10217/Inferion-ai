"""
Agents SDK Client Subsystem (Phase 5.36).
"""

from typing import Dict, Any, List, Optional
import httpx


class AgentsClient:
    def __init__(self, client: httpx.Client, base_url: str):
        self._client = client
        self.base_url = base_url

    def register(self, tenant_id: str, name: str, agent_type: str = "GENERAL", role: str = "TASK_EXECUTOR", capabilities: Optional[List[str]] = None, description: str = "") -> Dict[str, Any]:
        payload = {
            "name": name,
            "agent_type": agent_type,
            "role": role,
            "capabilities": capabilities or [],
            "description": description,
        }
        resp = self._client.post(f"{self.base_url}/v1/agents/register?tenant_id={tenant_id}", json=payload)
        resp.raise_for_status()
        return resp.json()

    def list(self, tenant_id: str = "default") -> List[Dict[str, Any]]:
        resp = self._client.get(f"{self.base_url}/v1/agents?tenant_id={tenant_id}")
        resp.raise_for_status()
        return resp.json().get("agents", [])

    def get(self, agent_id: str, tenant_id: str = "default") -> Dict[str, Any]:
        resp = self._client.get(f"{self.base_url}/v1/agents/{agent_id}?tenant_id={tenant_id}")
        resp.raise_for_status()
        return resp.json()

    def create_task(self, tenant_id: str, agent_id: str, goal: str, prompt: str, target_systems: Optional[List[str]] = None) -> Dict[str, Any]:
        payload = {
            "agent_id": agent_id,
            "goal": goal,
            "prompt": prompt,
            "target_systems": target_systems or [],
        }
        resp = self._client.post(f"{self.base_url}/v1/agents/tasks?tenant_id={tenant_id}", json=payload)
        resp.raise_for_status()
        return resp.json()

    def execute_task(self, tenant_id: str, goal: str, prompt: str, agent_id: Optional[str] = None, is_destructive: bool = False) -> Dict[str, Any]:
        payload = {
            "goal": goal,
            "prompt": prompt,
            "agent_id": agent_id,
            "is_destructive": is_destructive,
        }
        resp = self._client.post(f"{self.base_url}/v1/agents/execute?tenant_id={tenant_id}", json=payload)
        resp.raise_for_status()
        return resp.json()

    def get_trace(self, trace_id: str, tenant_id: str = "default") -> Dict[str, Any]:
        resp = self._client.get(f"{self.base_url}/v1/agents/traces/{trace_id}?tenant_id={tenant_id}")
        resp.raise_for_status()
        return resp.json()

    def get_analytics(self, tenant_id: str = "default") -> Dict[str, Any]:
        resp = self._client.get(f"{self.base_url}/v1/agents/analytics?tenant_id={tenant_id}")
        resp.raise_for_status()
        return resp.json()
