"""
Agent Scoped Execution Context
"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class AgentContext(BaseModel):
    organization_id: str = "default_org"
    workspace_id: Optional[str] = "default_workspace"
    user_id: str = "system"
    user_roles: List[str] = Field(default_factory=lambda: ["developer"])
    trace_id: Optional[str] = None
    session_id: Optional[str] = None
    request_id: Optional[str] = None
    auth_token: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
