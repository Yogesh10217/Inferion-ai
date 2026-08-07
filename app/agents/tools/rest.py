"""
REST Tool Executor Adapter
"""

import httpx
import logging
from typing import Dict, Any, Optional
from app.agents.agent_context import AgentContext

logger = logging.getLogger(__name__)


class RestToolAdapter:
    def __init__(self, endpoint_url: str, method: str = "POST", headers: Optional[Dict[str, str]] = None):
        self.endpoint_url = endpoint_url
        self.method = method.upper()
        self.headers = headers or {}

    async def execute(self, payload: Dict[str, Any], context: AgentContext) -> Dict[str, Any]:
        async with httpx.AsyncClient(timeout=30.0) as client:
            if self.method == "GET":
                resp = await client.get(self.endpoint_url, params=payload, headers=self.headers)
            else:
                resp = await client.post(self.endpoint_url, json=payload, headers=self.headers)
            resp.raise_for_status()
            try:
                return resp.json()
            except Exception:
                return {"text": resp.text, "status_code": resp.status_code}
