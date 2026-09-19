"""
Tool Definition Layer & Base Abstract Class for Enterprise Tool Calling Platform
"""

import abc
import asyncio
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.tools.tool_context import ToolContext
from app.tools.tool_result import ToolResult


class ToolCategory(str, Enum):
    BUILTIN = "builtin"
    INTEGRATION = "integration"
    MCP = "mcp"
    KNOWLEDGE = "knowledge"
    MEMORY = "memory"
    WORKFLOW = "workflow"
    AGENT = "agent"
    CUSTOM = "custom"


class ToolCapability(str, Enum):
    READ = "read"
    WRITE = "write"
    EXECUTE = "execute"
    NETWORK = "network"
    DATABASE = "database"
    HIGH_RISK = "high_risk"


class RetryPolicy(BaseModel):
    max_retries: int = Field(default=3, ge=0)
    initial_delay_seconds: float = Field(default=1.0, ge=0.0)
    backoff_factor: float = Field(default=2.0, ge=1.0)
    retryable_exceptions: List[str] = Field(
        default_factory=lambda: ["ToolTimeoutException", "ConnectionError", "HTTPError"]
    )


class ToolMetadata(BaseModel):
    name: str
    description: str
    version: str = "1.0.0"
    category: ToolCategory = ToolCategory.CUSTOM
    capabilities: List[ToolCapability] = Field(default_factory=lambda: [ToolCapability.READ])
    scopes: List[str] = Field(default_factory=lambda: ["tools:execute"])
    permissions: List[str] = Field(default_factory=list)
    cost_estimate: float = 0.0
    timeout: float = 30.0
    retry_policy: RetryPolicy = Field(default_factory=RetryPolicy)
    owner: str = "system"
    tenant_id: str = "default_tenant"
    parameters_schema: Dict[str, Any] = Field(default_factory=lambda: {"type": "object", "properties": {}})
    requires_approval: bool = False
    tags: List[str] = Field(default_factory=list)


class ToolDefinition(BaseModel):
    metadata: ToolMetadata
    handler: Optional[str] = None
    config: Dict[str, Any] = Field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()


class ToolExecutionRequest(BaseModel):
    tool_name: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    context: Optional[ToolContext] = None
    version: Optional[str] = None


class ToolExecutionResponse(BaseModel):
    result: ToolResult


class BaseTool(abc.ABC):
    """Abstract Base Class for all Tools registered in the Platform."""

    def __init__(self, metadata: ToolMetadata):
        self.metadata = metadata

    @property
    def name(self) -> str:
        return self.metadata.name

    @property
    def description(self) -> str:
        return self.metadata.description

    @property
    def version(self) -> str:
        return self.metadata.version

    @property
    def category(self) -> ToolCategory:
        return self.metadata.category

    @abc.abstractmethod
    async def execute_async(self, parameters: Dict[str, Any], context: ToolContext) -> ToolResult:
        """Asynchronously execute tool with parameters and context."""

    def execute(self, parameters: Dict[str, Any], context: ToolContext) -> ToolResult:
        """Synchronously execute tool (wraps execute_async)."""
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            # Running inside an active event loop
            import nest_asyncio

            nest_asyncio.apply()
            return loop.run_until_complete(self.execute_async(parameters, context))
        else:
            return asyncio.run(self.execute_async(parameters, context))
