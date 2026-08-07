"""
Tool Definition & Schema Models
"""

from typing import Dict, Any, List, Optional, Callable, Awaitable
from pydantic import BaseModel, Field


class ToolParameter(BaseModel):
    name: str
    type: str  # string, integer, number, boolean, object, array
    description: str
    required: bool = True
    default: Optional[Any] = None


class ToolDefinition(BaseModel):
    name: str
    description: str
    parameters: List[ToolParameter] = Field(default_factory=list)
    permissions: List[str] = Field(default_factory=list)
    timeout_seconds: float = 30.0
    max_retries: int = 2
    cost_estimate_dollars: float = 0.0
    required_scopes: List[str] = Field(default_factory=list)
    tool_type: str = "builtin"  # builtin, plugin, rest, python, shell
