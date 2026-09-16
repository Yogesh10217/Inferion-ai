"""Agent Task Management Subsystem (Phase 5.36)."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Set

from pydantic import BaseModel, Field

from app.agent_orchestration.exceptions import (
    AgentTaskNotFoundException,
    CrossTenantAgentAccessException,
    InvalidAgentExecutionTransitionException,
)
from app.platform_contracts.tenant import TenantAccessGuard


class AgentTaskType(str, Enum):
    ANALYSIS = "ANALYSIS"
    PLANNING = "PLANNING"
    EXECUTION = "EXECUTION"
    COLLABORATION = "COLLABORATION"
    INVESTIGATION = "INVESTIGATION"
    RECOVERY = "RECOVERY"


class AgentTaskStatus(str, Enum):
    CREATED = "CREATED"
    VALIDATING = "VALIDATING"
    PLANNING = "PLANNING"
    GOVERNANCE_PENDING = "GOVERNANCE_PENDING"
    APPROVAL_PENDING = "APPROVAL_PENDING"
    READY = "READY"
    EXECUTING = "EXECUTING"
    VERIFYING = "VERIFYING"
    COMPLETED = "COMPLETED"

    # Terminal / Exception States
    BLOCKED = "BLOCKED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    ESCALATED = "ESCALATED"


class AgentTaskPriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class AgentTaskInput(BaseModel):
    goal: str
    prompt: str
    target_systems: List[str] = Field(default_factory=list)
    parameters: Dict[str, Any] = Field(default_factory=dict)


class AgentTaskContext(BaseModel):
    context_id: Optional[str] = None
    knowledge_references: List[str] = Field(default_factory=list)
    constraints: Dict[str, Any] = Field(default_factory=dict)


class AgentTaskResult(BaseModel):
    is_successful: bool = False
    output_summary: str = ""
    trace_id: Optional[str] = None
    snapshot_id: Optional[str] = None
    evidence_references: List[str] = Field(default_factory=list)
    execution_metrics: Dict[str, Any] = Field(default_factory=dict)
    error_message: Optional[str] = None


class AgentTask(BaseModel):
    task_id: str = Field(default_factory=lambda: f"task_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    agent_id: str
    task_type: AgentTaskType = AgentTaskType.EXECUTION
    priority: AgentTaskPriority = AgentTaskPriority.MEDIUM
    status: AgentTaskStatus = AgentTaskStatus.CREATED
    input_data: AgentTaskInput
    context: AgentTaskContext = Field(default_factory=AgentTaskContext)
    result: Optional[AgentTaskResult] = None
    assigned_plan_id: Optional[str] = None
    assigned_execution_id: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AgentTaskManager:
    """Manages Agent Task creation, state machine transitions, and retrieval."""

    VALID_TRANSITIONS: Dict[AgentTaskStatus, Set[AgentTaskStatus]] = {
        AgentTaskStatus.CREATED: {AgentTaskStatus.VALIDATING, AgentTaskStatus.CANCELLED},
        AgentTaskStatus.VALIDATING: {AgentTaskStatus.PLANNING, AgentTaskStatus.BLOCKED, AgentTaskStatus.FAILED, AgentTaskStatus.CANCELLED},
        AgentTaskStatus.PLANNING: {AgentTaskStatus.GOVERNANCE_PENDING, AgentTaskStatus.READY, AgentTaskStatus.BLOCKED, AgentTaskStatus.FAILED, AgentTaskStatus.CANCELLED},
        AgentTaskStatus.GOVERNANCE_PENDING: {AgentTaskStatus.APPROVAL_PENDING, AgentTaskStatus.READY, AgentTaskStatus.BLOCKED, AgentTaskStatus.FAILED, AgentTaskStatus.CANCELLED},
        AgentTaskStatus.APPROVAL_PENDING: {AgentTaskStatus.READY, AgentTaskStatus.BLOCKED, AgentTaskStatus.CANCELLED, AgentTaskStatus.ESCALATED},
        AgentTaskStatus.READY: {AgentTaskStatus.EXECUTING, AgentTaskStatus.CANCELLED},
        AgentTaskStatus.EXECUTING: {AgentTaskStatus.VERIFYING, AgentTaskStatus.BLOCKED, AgentTaskStatus.FAILED, AgentTaskStatus.ESCALATED, AgentTaskStatus.CANCELLED},
        AgentTaskStatus.VERIFYING: {AgentTaskStatus.COMPLETED, AgentTaskStatus.FAILED, AgentTaskStatus.ESCALATED},

        # Terminal states can transition to ESCALATED or RECOVERY
        AgentTaskStatus.BLOCKED: {AgentTaskStatus.ESCALATED, AgentTaskStatus.CANCELLED, AgentTaskStatus.VALIDATING},
        AgentTaskStatus.FAILED: {AgentTaskStatus.ESCALATED, AgentTaskStatus.CANCELLED, AgentTaskStatus.VALIDATING},
        AgentTaskStatus.COMPLETED: set(),
        AgentTaskStatus.CANCELLED: set(),
        AgentTaskStatus.ESCALATED: {AgentTaskStatus.VALIDATING, AgentTaskStatus.CANCELLED},
    }

    def __init__(self, tenant_guard: Optional[TenantAccessGuard] = None) -> None:
        self.tenant_guard = tenant_guard or TenantAccessGuard()
        self._tasks: Dict[str, AgentTask] = {}

    def create_task(
        self,
        tenant_id: str,
        agent_id: str,
        goal: str,
        prompt: str,
        task_type: AgentTaskType = AgentTaskType.EXECUTION,
        priority: AgentTaskPriority = AgentTaskPriority.MEDIUM,
        target_systems: Optional[List[str]] = None,
        parameters: Optional[Dict[str, Any]] = None,
        task_id: Optional[str] = None,
    ) -> AgentTask:
        tid = task_id or f"task_{uuid.uuid4().hex[:12]}"
        task = AgentTask(
            task_id=tid,
            tenant_id=tenant_id,
            agent_id=agent_id,
            task_type=task_type,
            priority=priority,
            status=AgentTaskStatus.CREATED,
            input_data=AgentTaskInput(
                goal=goal,
                prompt=prompt,
                target_systems=target_systems or [],
                parameters=parameters or {},
            ),
        )
        self._tasks[task.task_id] = task
        return task

    def get_task(self, task_id: str, tenant_id: str) -> AgentTask:
        task = self._tasks.get(task_id)
        if not task:
            raise AgentTaskNotFoundException(task_id)

        try:
            self.tenant_guard.enforce_isolation(tenant_id, task.tenant_id)
        except Exception:
            raise CrossTenantAgentAccessException(tenant_id, task.tenant_id)

        return task

    def list_tasks(
        self,
        tenant_id: str,
        agent_id: Optional[str] = None,
        status: Optional[AgentTaskStatus] = None,
    ) -> List[AgentTask]:
        results = []
        for task in self._tasks.values():
            if task.tenant_id == tenant_id or tenant_id == "global":
                if agent_id and task.agent_id != agent_id:
                    continue
                if status and task.status != status:
                    continue
                results.append(task)
        return results

    def transition_task_status(
        self,
        task_id: str,
        tenant_id: str,
        new_status: AgentTaskStatus,
        result: Optional[AgentTaskResult] = None,
    ) -> AgentTask:
        task = self.get_task(task_id, tenant_id)
        current = task.status

        allowed = self.VALID_TRANSITIONS.get(current, set())
        if new_status not in allowed and new_status != current:
            raise InvalidAgentExecutionTransitionException(current.value, new_status.value)

        task.status = new_status
        task.updated_at = datetime.now(timezone.utc)
        if result:
            task.result = result
        return task
