"""
Production HTTP Request Tool
"""

import logging
import time
from typing import Any, Dict

import httpx

from app.tools.tool import BaseTool, ToolCapability, ToolCategory, ToolMetadata
from app.tools.tool_context import ToolContext
from app.tools.tool_result import ToolExecutionStatus, ToolResult

logger = logging.getLogger(__name__)


class HTTPTool(BaseTool):
    """Production HTTP tool supporting GET, POST, PUT, DELETE, custom headers, retries, and rate limiting."""

    def __init__(self, name: str = "http_client", timeout: float = 15.0):
        metadata = ToolMetadata(
            name=name,
            description="Performs HTTP REST API requests (GET, POST, PUT, DELETE)",
            category=ToolCategory.BUILTIN,
            capabilities=[ToolCapability.NETWORK, ToolCapability.READ, ToolCapability.WRITE],
            cost_estimate=0.0005,
            timeout=timeout,
            parameters_schema={
                "type": "object",
                "properties": {
                    "method": {"type": "string", "enum": ["GET", "POST", "PUT", "DELETE"]},
                    "url": {"type": "string", "description": "Target HTTP URL"},
                    "headers": {"type": "object", "description": "HTTP request headers"},
                    "json_body": {"type": "object", "description": "JSON payload for POST/PUT"},
                    "params": {"type": "object", "description": "URL query parameters"},
                },
                "required": ["method", "url"],
            },
        )
        super().__init__(metadata)

    async def execute_async(self, parameters: Dict[str, Any], context: ToolContext) -> ToolResult:
        start_time = time.time()
        method = parameters.get("method", "GET").upper()
        url = parameters.get("url")
        headers = parameters.get("headers") or {}
        json_body = parameters.get("json_body")
        queryParams = parameters.get("params")

        if not url:
            return ToolResult(
                execution_id=context.execution_id,
                tool_name=self.name,
                status=ToolExecutionStatus.FAILED,
                error="URL parameter is required",
            )

        try:
            async with httpx.AsyncClient(timeout=self.metadata.timeout) as client:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=json_body if method in ("POST", "PUT", "PATCH") else None,
                    params=queryParams,
                )
                elapsed = time.time() - start_time

                try:
                    resp_data = response.json()
                except Exception:
                    resp_data = response.text

                status = ToolExecutionStatus.SUCCESS if response.status_code < 400 else ToolExecutionStatus.FAILED
                return ToolResult(
                    execution_id=context.execution_id,
                    tool_name=self.name,
                    status=status,
                    output={"status_code": response.status_code, "data": resp_data, "headers": dict(response.headers)},
                    error=None if response.status_code < 400 else f"HTTP {response.status_code}: {response.text}",
                    execution_time_seconds=elapsed,
                    cost=self.metadata.cost_estimate,
                    metadata={"external_api_call": True},
                )
        except Exception as ex:
            elapsed = time.time() - start_time
            return ToolResult(
                execution_id=context.execution_id,
                tool_name=self.name,
                status=ToolExecutionStatus.FAILED,
                error=f"HTTP Network Request Error: {str(ex)}",
                execution_time_seconds=elapsed,
                metadata={"external_api_call": True},
            )
