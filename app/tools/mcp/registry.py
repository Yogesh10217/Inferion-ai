"""
MCP Registry for Managing Multiple MCP Client/Server Connections
"""

import logging
import threading
from typing import Any, Dict, Optional

from app.tools.exceptions import MCPException
from app.tools.mcp.client import MCPClient
from app.tools.mcp.server import MCPServer
from app.tools.mcp.transport import InMemoryTransport, MCPTransport

logger = logging.getLogger(__name__)


class MCPRegistry:
    """Registry maintaining connected MCP servers, client sessions, and health checks."""

    def __init__(self):
        self._lock = threading.RLock()
        self._clients: Dict[str, MCPClient] = {}
        self._servers: Dict[str, MCPServer] = {}

    def register_server(self, server_id: str, server_or_transport: Any) -> MCPClient:
        """Register an in-memory MCPServer or transport and return a connected MCPClient."""
        with self._lock:
            if isinstance(server_or_transport, MCPServer):
                server = server_or_transport
                self._servers[server_id] = server
                transport = InMemoryTransport(server)
            elif isinstance(server_or_transport, MCPTransport):
                transport = server_or_transport
            else:
                raise MCPException("server_or_transport must be an MCPServer or MCPTransport instance")

            client = MCPClient(transport=transport, client_name=f"client-{server_id}")
            self._clients[server_id] = client
            logger.info(f"Registered MCP server session '{server_id}'")
            return client

    def remove_server(self, server_id: str) -> bool:
        """Remove and close an MCP server session."""
        with self._lock:
            client = self._clients.pop(server_id, None)
            self._servers.pop(server_id, None)
            if client:
                import asyncio

                try:
                    asyncio.create_task(client.close())
                except RuntimeError:
                    pass
                return True
            return False

    def get_client(self, server_id: str) -> Optional[MCPClient]:
        with self._lock:
            return self._clients.get(server_id)

    async def discover_capabilities(self) -> Dict[str, Any]:
        """Aggregate tools, resources, and prompts across all registered MCP servers."""
        with self._lock:
            client_items = list(self._clients.items())

        capabilities_map = {}
        for sid, client in client_items:
            try:
                tools = await client.discover_tools()
                resources = await client.list_resources()
                prompts = await client.get_prompts()
                capabilities_map[sid] = {
                    "tools": [t.model_dump() for t in tools],
                    "resources": [r.model_dump() for r in resources],
                    "prompts": [p.model_dump() for p in prompts],
                }
            except Exception as e:
                logger.warning(f"Failed to discover capabilities for server '{sid}': {e}")
                capabilities_map[sid] = {"error": str(e)}

        return capabilities_map

    async def health_monitoring(self) -> Dict[str, Any]:
        """Check health status across all registered MCP clients."""
        with self._lock:
            client_items = list(self._clients.items())

        health_map = {}
        for sid, client in client_items:
            is_healthy = await client.health_check()
            health_map[sid] = {"status": "healthy" if is_healthy else "unhealthy"}
        return health_map
