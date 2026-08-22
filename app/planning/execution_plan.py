"""
Execution Plan Model Representation
"""

import uuid
import time
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from app.planning.goals import Goal, Objective, Milestone, Task


class ExecutionPlan(BaseModel):
    plan_id: str = Field(default_factory=lambda: f"plan_{uuid.uuid4().hex[:12]}")
    goal_id: str
    title: str
    tenant_id: str = "default_tenant"
    workspace_id: str = "default_workspace"
    objectives: List[Objective] = Field(default_factory=list)
    milestones: List[Milestone] = Field(default_factory=list)
    tasks: List[Task] = Field(default_factory=list)
    execution_order: List[str] = Field(default_factory=list)  # task_ids
    critical_path: List[str] = Field(default_factory=list)
    estimated_duration_seconds: float = 0.0
    estimated_cost: float = 0.0
    confidence_score: float = 0.9
    status: str = "draft"  # draft, approved, executing, completed, failed
    created_at: float = Field(default_factory=time.time)
