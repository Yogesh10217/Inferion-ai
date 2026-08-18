"""
JSON-RPC 2.0 & Model Context Protocol (MCP) Schemas
"""

from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field


class MCPJsonRpcRequest(BaseModel):
    jsonrpc: str = "2.0"
    id: Union[str, int]
    method: str
    params: Optional[Dict[str, Any]] = None


class MCPJsonRpcResponse(BaseModel):
    jsonrpc: str = "2.0"
    id: Union[str, int]
    result: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None


class MCPToolSchema(BaseModel):
    name: str
    description: str
    inputSchema: Dict[str, Any] = Field(default_factory=dict)


class MCPResourceSchema(BaseModel):
    uri: str
    name: str
    description: Optional[str] = None
    mimeType: Optional[str] = "text/plain"


class MCPPromptArgument(BaseModel):
    name: str
    description: Optional[str] = None
    required: bool = False


class MCPPromptSchema(BaseModel):
    name: str
    description: Optional[str] = None
    arguments: List[MCPPromptArgument] = Field(default_factory=list)


class MCPCapabilities(BaseModel):
    tools: Dict[str, Any] = Field(default_factory=lambda: {"listChanged": True})
    resources: Dict[str, Any] = Field(default_factory=lambda: {"subscribe": True, "listChanged": True})
    prompts: Dict[str, Any] = Field(default_factory=lambda: {"listChanged": True})
    logging: Dict[str, Any] = Field(default_factory=dict)


class MCPServerInfo(BaseModel):
    name: str
    version: str = "1.0.0"


class MCPClientInfo(BaseModel):
    name: str = "llm-engine-mcp-client"
    version: str = "1.0.0"
