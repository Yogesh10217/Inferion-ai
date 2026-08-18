"""
MCP Client Implementation for Model Context Protocol Platform
"""

import uuid
import logging
from typing import Dict, Any, List, Optional

from app.tools.mcp.schemas import (
    MCPJsonRpcRequest,
    MCPJsonRpcResponse,
    MCPToolSchema,
    MCPResourceSchema,
    MCPPromptSchema,
)
from app.tools.mcp.transport import MCPTransport
from app.tools.exceptions import MCPConnectionError, MCPToolError, MCPResourceError, MCPPromptError

logger = logging.getLogger(__name__)


class MCPClient:
    """Production-grade MCP Client implementing tool, resource, and prompt discovery and execution."""

    def __init__(self, transport: MCPTransport, client_name: str = "llm-engine-mcp"):
        self.transport = transport
        self.client_name = client_name
        self.is_connected = False

    async def connect(self) -> None:
        """Initialize connection and negotiate capabilities with remote server."""
        await self.transport.connect()
        self.is_connected = True

        # Perform initialize handshake
        req = MCPJsonRpcRequest(
            id=1,
            method="initialize",
            params={
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}, "resources": {}, "prompts": {}},
                "clientInfo": {"name": self.client_name, "version": "1.0.0"},
            },
        )
        res = await self.transport.send_request(req)
        if res.error:
            raise MCPConnectionError(f"MCP Initialization failed: {res.error}")

    async def close(self) -> None:
        """Close connection."""
        if self.is_connected:
            await self.transport.close()
            self.is_connected = False

    async def discover_tools(self) -> List[MCPToolSchema]:
        """Discover tools available on remote server."""
        if not self.is_connected:
            await self.connect()

        req = MCPJsonRpcRequest(id=uuid.uuid4().hex[:8], method="tools/list", params={})
        res = await self.transport.send_request(req)
        if res.error:
            raise MCPToolError(f"Failed to discover tools: {res.error}")

        tools_data = res.result.get("tools", []) if isinstance(res.result, dict) else []
        return [MCPToolSchema(**t) for t in tools_data]

    async def execute_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool on the remote server."""
        if not self.is_connected:
            await self.connect()

        req = MCPJsonRpcRequest(
            id=uuid.uuid4().hex[:8],
            method="tools/call",
            params={"name": name, "arguments": arguments},
        )
        res = await self.transport.send_request(req)
        if res.error:
            raise MCPToolError(f"Tool execution '{name}' failed: {res.error}")

        return res.result if isinstance(res.result, dict) else {"content": res.result}

    async def list_resources(self) -> List[MCPResourceSchema]:
        """List resources exported by server."""
        if not self.is_connected:
            await self.connect()

        req = MCPJsonRpcRequest(id=uuid.uuid4().hex[:8], method="resources/list", params={})
        res = await self.transport.send_request(req)
        if res.error:
            raise MCPResourceError(f"Failed to list resources: {res.error}")

        resources = res.result.get("resources", []) if isinstance(res.result, dict) else []
        return [MCPResourceSchema(**r) for r in resources]

    async def get_prompts(self) -> List[MCPPromptSchema]:
        """List prompt templates exposed by server."""
        if not self.is_connected:
            await self.connect()

        req = MCPJsonRpcRequest(id=uuid.uuid4().hex[:8], method="prompts/list", params={})
        res = await self.transport.send_request(req)
        if res.error:
            raise MCPPromptError(f"Failed to list prompts: {res.error}")

        prompts = res.result.get("prompts", []) if isinstance(res.result, dict) else []
        return [MCPPromptSchema(**p) for p in prompts]

    async def health_check(self) -> bool:
        """Check connection and server status via ping."""
        try:
            if not self.is_connected:
                await self.connect()

            req = MCPJsonRpcRequest(id="ping", method="ping", params={})
            res = await self.transport.send_request(req)
            return res.error is None
        except Exception as e:
            logger.warning(f"MCP health check failed: {e}")
            return False
