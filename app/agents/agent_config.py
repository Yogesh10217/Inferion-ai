"""
Agent Configuration Models
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class AgentConfig(BaseModel):
    name: str
    description: str
    system_prompt: str
    model: str = "gpt-4o-mini"
    provider: Optional[str] = None
    planner_strategy: str = "react"  # zeroshot, react, plan_execute, tree_of_thought
    reflection_strategy: str = "self_critique"  # simple, self_critique, llm_judge
    tools: List[str] = Field(default_factory=list)
    max_iterations: int = 15
    max_cost_dollars: Optional[float] = None
    max_tokens: Optional[int] = None
    enable_memory: bool = True
    enable_reflection: bool = True
    enable_cache: bool = True
    require_approval_tools: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
