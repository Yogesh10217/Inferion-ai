"""
MCP Server Implementation for Model Context Protocol Subsystem
"""

import inspect
import logging
from typing import Any, Callable, Dict, Optional, Tuple

from app.tools.mcp.schemas import (
    MCPCapabilities,
    MCPJsonRpcRequest,
    MCPJsonRpcResponse,
    MCPPromptSchema,
    MCPResourceSchema,
    MCPServerInfo,
    MCPToolSchema,
)

logger = logging.getLogger(__name__)


class MCPServer:
    """Production-grade MCP Server exporting local tools, resources, and prompts over JSON-RPC 2.0."""

    def __init__(self, name: str = "llm-engine-mcp-server", version: str = "1.0.0"):
        self.server_info = MCPServerInfo(name=name, version=version)
        self._tools: Dict[str, Tuple[MCPToolSchema, Callable]] = {}
        self._resources: Dict[str, MCPResourceSchema] = {}
        self._prompts: Dict[str, MCPPromptSchema] = {}

    def register_tool(self, name: str, description: str, handler: Callable, input_schema: Optional[Dict[str, Any]] = None) -> None:
        schema = MCPToolSchema(
            name=name,
            description=description,
            inputSchema=input_schema or {"type": "object", "properties": {}},
        )
        self._tools[name] = (schema, handler)
        logger.info(f"Registered MCP Tool '{name}' on server '{self.server_info.name}'")

    def register_resource(self, uri: str, name: str, description: Optional[str] = None, mime_type: str = "text/plain") -> None:
        resource = MCPResourceSchema(uri=uri, name=name, description=description, mimeType=mime_type)
        self._resources[uri] = resource
        logger.info(f"Registered MCP Resource '{uri}'")

    def register_prompt(self, name: str, description: Optional[str] = None, arguments: Optional[list] = None) -> None:
        prompt = MCPPromptSchema(name=name, description=description, arguments=arguments or [])
        self._prompts[name] = prompt
        logger.info(f"Registered MCP Prompt '{name}'")

    def capabilities(self) -> MCPCapabilities:
        return MCPCapabilities()

    def health(self) -> Dict[str, Any]:
        return {
            "status": "healthy",
            "server": self.server_info.model_dump(),
            "tools_count": len(self._tools),
            "resources_count": len(self._resources),
            "prompts_count": len(self._prompts),
        }

    async def handle_request(self, request: MCPJsonRpcRequest) -> MCPJsonRpcResponse:
        """Handle incoming JSON-RPC 2.0 request."""
        method = request.method
        req_id = request.id
        params = request.params or {}

        try:
            if method == "initialize":
                return MCPJsonRpcResponse(
                    id=req_id,
                    result={
                        "protocolVersion": "2024-11-05",
                        "capabilities": self.capabilities().model_dump(),
                        "serverInfo": self.server_info.model_dump(),
                    },
                )
            elif method == "ping":
                return MCPJsonRpcResponse(id=req_id, result={"status": "pong"})
            elif method == "tools/list":
                tools_list = [schema.model_dump() for schema, _ in self._tools.values()]
                return MCPJsonRpcResponse(id=req_id, result={"tools": tools_list})
            elif method == "tools/call":
                tname = params.get("name")
                args = params.get("arguments", {})
                if tname not in self._tools:
                    return MCPJsonRpcResponse(
                        id=req_id,
                        error={"code": -32601, "message": f"Tool '{tname}' not found"},
                    )
                schema, handler = self._tools[tname]
                if inspect.iscoroutinefunction(handler):
                    output = await handler(**args)
                else:
                    output = handler(**args)
                return MCPJsonRpcResponse(id=req_id, result={"content": [{"type": "text", "text": str(output)}]})
            elif method == "resources/list":
                res_list = [r.model_dump() for r in self._resources.values()]
                return MCPJsonRpcResponse(id=req_id, result={"resources": res_list})
            elif method == "prompts/list":
                p_list = [p.model_dump() for p in self._prompts.values()]
                return MCPJsonRpcResponse(id=req_id, result={"prompts": p_list})
            else:
                return MCPJsonRpcResponse(
                    id=req_id,
                    error={"code": -32601, "message": f"Method '{method}' not supported"},
                )
        except Exception as e:
            return MCPJsonRpcResponse(
                id=req_id,
                error={"code": -32603, "message": f"Internal server error: {str(e)}"},
            )
