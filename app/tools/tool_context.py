"""
Execution Context Model for Enterprise Tool Calling Subsystem
"""

import uuid
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ToolContext(BaseModel):
    """Execution context containing tenant isolation, RBAC credentials, and tracing metadata."""
    execution_id: str = Field(default_factory=lambda: f"exec_{uuid.uuid4().hex[:12]}")
    tenant_id: str = Field(default="default_tenant")
    organization_id: str = Field(default="default_org")
    workspace_id: str = Field(default="default_workspace")
    user_id: str = Field(default="anonymous")
    user_role: str = Field(default="user")
    user_scopes: List[str] = Field(default_factory=lambda: ["tools:read", "tools:execute"])
    trace_id: Optional[str] = Field(default=None)
    span_id: Optional[str] = Field(default=None)
    budget_limit: Optional[float] = Field(default=None)
    custom_headers: Dict[str, str] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()
