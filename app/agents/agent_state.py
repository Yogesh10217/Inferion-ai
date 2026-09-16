"""
Agent Execution State Machine Models & Enums
"""

import time
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class AgentStatus(str, Enum):
    INITIALIZING = "INITIALIZING"
    PLANNING = "PLANNING"
    EXECUTING_TOOL = "EXECUTING_TOOL"
    AWAITING_APPROVAL = "AWAITING_APPROVAL"
    REFLECTING = "REFLECTING"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class StepType(str, Enum):
    PLAN = "PLAN"
    TOOL_CALL = "TOOL_CALL"
    OBSERVATION = "OBSERVATION"
    REFLECTION = "REFLECTION"
    MEMORY_UPDATE = "MEMORY_UPDATE"
    FINAL_RESPONSE = "FINAL_RESPONSE"


class ExecutionStep(BaseModel):
    step_id: str
    step_type: StepType
    iteration: int
    title: str
    input_data: Dict[str, Any] = Field(default_factory=dict)
    output_data: Dict[str, Any] = Field(default_factory=dict)
    status: str = "SUCCESS"
    error: Optional[str] = None
    duration_ms: float = 0.0
    timestamp: float = Field(default_factory=time.time)


class AgentState(BaseModel):
    session_id: str
    agent_id: str
    status: AgentStatus = AgentStatus.INITIALIZING
    current_iteration: int = 0
    max_iterations: int = 15
    plan_steps: List[Dict[str, Any]] = Field(default_factory=list)
    current_step_index: int = 0
    execution_history: List[ExecutionStep] = Field(default_factory=list)
    pending_approval: Optional[Dict[str, Any]] = None
    final_output: Optional[str] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
