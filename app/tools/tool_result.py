"""
Tool Execution Result Model for Enterprise Tool Calling Subsystem
"""

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ToolExecutionStatus(str, Enum):
    SUCCESS = "success"
    FAILED = "failed"
    PENDING_APPROVAL = "pending_approval"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


class ToolResult(BaseModel):
    """Encapsulates execution output, diagnostic metrics, telemetry, and status."""

    execution_id: str
    tool_name: str
    status: ToolExecutionStatus = ToolExecutionStatus.SUCCESS
    output: Optional[Any] = None
    error: Optional[str] = None
    execution_time_seconds: float = 0.0
    cost: float = 0.0
    compute_usage: Dict[str, Any] = Field(default_factory=lambda: {"cpu_ms": 0.0, "memory_mb": 0.0})
    storage_usage: Dict[str, Any] = Field(default_factory=lambda: {"bytes_read": 0, "bytes_written": 0})
    logs: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    artifacts: List[Dict[str, Any]] = Field(default_factory=list)

    def is_success(self) -> bool:
        return self.status == ToolExecutionStatus.SUCCESS

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()
