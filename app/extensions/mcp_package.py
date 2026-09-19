"""MCP Package Ecosystem integrating Model Context Protocol servers."""

import logging
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from app.tools.mcp.registry import MCPRegistry
from app.tools.mcp.server import MCPServer

logger = logging.getLogger(__name__)


class MCPServerManifest(BaseModel):
    """MCP Server package specification."""

    package_name: str
    version: str = "1.0.0"
    server_type: str = "STDIO"  # 'STDIO', 'SSE'
    command: str = "python"
    args: List[str] = Field(default_factory=list)
    env: Dict[str, str] = Field(default_factory=dict)
    capabilities: List[str] = Field(default_factory=list)


class MCPPackage(BaseModel):
    """Managed MCP Package entity."""

    package_id: str
    manifest: MCPServerManifest
    tenant_id: str = "global"
    is_active: bool = True


class MCPPackageManager:
    """Manages MCP Server packages and registers them into the core MCPRegistry."""

    def __init__(self, mcp_registry: Optional[MCPRegistry] = None) -> None:
        self.mcp_registry = mcp_registry or MCPRegistry()

    def register_mcp_package(self, package: MCPPackage) -> MCPServer:
        """Register MCP Package into core platform MCPRegistry."""
        server = MCPServer(
            name=package.manifest.package_name,
            version=package.manifest.version,
        )

        self.mcp_registry.register_server(package.package_id, server)
        logger.info(
            f"[MCP PACKAGE MANAGER] Registered MCP server package '{package.manifest.package_name}' (ID: {package.package_id})"
        )
        return server
