"""
Goal and Task Hierarchy Representation Models
"""

import time
import uuid
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class Status(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"


class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SubTask(BaseModel):
    subtask_id: str = Field(default_factory=lambda: f"subtask_{uuid.uuid4().hex[:8]}")
    title: str
    description: str = ""
    status: Status = Status.PENDING
    assigned_agent: Optional[str] = None


class Task(BaseModel):
    task_id: str = Field(default_factory=lambda: f"task_{uuid.uuid4().hex[:8]}")
    title: str
    description: str = ""
    priority: Priority = Priority.MEDIUM
    status: Status = Status.PENDING
    subtasks: List[SubTask] = Field(default_factory=list)
    dependencies: List[str] = Field(default_factory=list)  # task_ids
    estimated_cost: float = 0.01
    estimated_duration_seconds: float = 10.0


class Milestone(BaseModel):
    milestone_id: str = Field(default_factory=lambda: f"ms_{uuid.uuid4().hex[:8]}")
    title: str
    description: str = ""
    tasks: List[Task] = Field(default_factory=list)
    target_completion_percent: float = 100.0
    status: Status = Status.PENDING


class Objective(BaseModel):
    objective_id: str = Field(default_factory=lambda: f"obj_{uuid.uuid4().hex[:8]}")
    title: str
    milestones: List[Milestone] = Field(default_factory=list)
    status: Status = Status.PENDING


class Goal(BaseModel):
    goal_id: str = Field(default_factory=lambda: f"goal_{uuid.uuid4().hex[:10]}")
    title: str
    description: str = ""
    tenant_id: str = "default_tenant"
    workspace_id: str = "default_workspace"
    user_id: str = "anonymous"
    objectives: List[Objective] = Field(default_factory=list)
    status: Status = Status.PENDING
    created_at: float = Field(default_factory=time.time)
