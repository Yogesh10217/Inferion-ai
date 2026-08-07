"""
Agents SDK Client Subsystem
"""

from typing import Dict, Any, List, Optional
import httpx


class AgentsClient:
    def __init__(self, client: httpx.Client, base_url: str):
        self._client = client
        self.base_url = base_url

    def create(self, agent_id: str, name: str, description: str = "", system_prompt: str = "You are a helpful agent.", **kwargs) -> Dict[str, Any]:
        payload = {
            "id": agent_id,
            "name": name,
            "description": description,
            "system_prompt": system_prompt,
            **kwargs
        }
        resp = self._client.post(f"{self.base_url}/v1/agents", json=payload)
        resp.raise_for_status()
        return resp.json()

    def list(self) -> List[Dict[str, Any]]:
        resp = self._client.get(f"{self.base_url}/v1/agents")
        resp.raise_for_status()
        return resp.json()

    def get(self, agent_id: str) -> Dict[str, Any]:
        resp = self._client.get(f"{self.base_url}/v1/agents/{agent_id}")
        resp.raise_for_status()
        return resp.json()

    def run(self, agent_id: str, prompt: str) -> Dict[str, Any]:
        resp = self._client.post(f"{self.base_url}/v1/agents/{agent_id}/run", json={"prompt": prompt})
        resp.raise_for_status()
        return resp.json()

    def resume(self, session_id: str, approved: Optional[bool] = None) -> Dict[str, Any]:
        payload = {"approved": approved} if approved is not None else {}
        resp = self._client.post(f"{self.base_url}/v1/agents/sessions/{session_id}/resume", json=payload)
        resp.raise_for_status()
        return resp.json()

    def cancel(self, session_id: str) -> Dict[str, Any]:
        resp = self._client.post(f"{self.base_url}/v1/agents/sessions/{session_id}/cancel")
        resp.raise_for_status()
        return resp.json()
