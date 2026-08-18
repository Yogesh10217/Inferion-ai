"""
Agent Profile Configuration Model
"""

import uuid
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from app.multi_agent.agent_role import AgentRole, RoleType


class AgentProfile(BaseModel):
    """Profile specification for an individual agent in a team."""
    agent_id: str = Field(default_factory=lambda: f"agent_{uuid.uuid4().hex[:10]}")
    name: str
    role: AgentRole = Field(default_factory=lambda: AgentRole.get_preset_role(RoleType.EXECUTOR))
    system_prompt: str = "You are a specialized AI agent team member."
    model_name: str = "default-llm"
    temperature: float = 0.7
    max_iterations: int = 10
    cost_rate_per_token: float = 0.000002
    capabilities: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
