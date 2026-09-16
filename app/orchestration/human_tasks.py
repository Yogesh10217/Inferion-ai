"""Human-in-the-Loop Task Platform & SLA Escalation Subsystem."""

import logging
import uuid
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.approvals.approval_engine import ApprovalEngine
from app.orchestration.exceptions import TaskAssignmentException

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class TaskStatus(str, Enum):
    CREATED = "CREATED"
    ASSIGNED = "ASSIGNED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    ESCALATED = "ESCALATED"
    DELEGATED = "DELEGATED"
    EXPIRED = "EXPIRED"
    CANCELLED = "CANCELLED"


class TaskPriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class HumanTask(BaseModel):
    task_id: str = Field(default_factory=lambda: f"htask_{uuid.uuid4().hex[:10]}")
    title: str
    tenant_id: str = "global"
    case_id: Optional[str] = None
    execution_id: Optional[str] = None

    assigned_user_id: Optional[str] = None
    assigned_role: Optional[str] = None
    status: TaskStatus = TaskStatus.CREATED
    priority: TaskPriority = TaskPriority.MEDIUM

    inputs: Dict[str, Any] = Field(default_factory=dict)
    outputs: Dict[str, Any] = Field(default_factory=dict)

    created_at: datetime = Field(default_factory=_now)
    due_at: Optional[datetime] = Field(default_factory=lambda: _now() + timedelta(hours=24))
    completed_at: Optional[datetime] = None


class HumanTaskManager:
    """Manages human-in-the-loop task assignments, SLA deadlines, escalations, and approvals."""

    def __init__(self, approval_engine: Optional[ApprovalEngine] = None) -> None:
        self.approval_engine = approval_engine or ApprovalEngine()
        self._tasks: Dict[str, HumanTask] = {}

    def create_task(
        self,
        title: str,
        assigned_user_id: Optional[str] = None,
        assigned_role: Optional[str] = None,
        tenant_id: str = "global",
        case_id: Optional[str] = None,
        execution_id: Optional[str] = None,
        priority: TaskPriority = TaskPriority.MEDIUM,
    ) -> HumanTask:
        task = HumanTask(
            title=title,
            assigned_user_id=assigned_user_id,
            assigned_role=assigned_role,
            tenant_id=tenant_id,
            case_id=case_id,
            execution_id=execution_id,
            priority=priority,
            status=TaskStatus.ASSIGNED if assigned_user_id else TaskStatus.CREATED,
        )
        self._tasks[task.task_id] = task
        logger.info(f"[HUMAN TASK MANAGER] Created task '{task.task_id}' ('{title}') assigned to user '{assigned_user_id}' (Tenant: {tenant_id})")
        return task

    def complete_task(self, task_id: str, outputs: Optional[Dict[str, Any]] = None) -> HumanTask:
        task = self.get_task(task_id)
        task.status = TaskStatus.COMPLETED
        task.outputs = outputs or {}
        task.completed_at = _now()
        logger.info(f"[HUMAN TASK MANAGER] Task '{task_id}' COMPLETED")
        return task

    def escalate_task(self, task_id: str, escalation_reason: str = "SLA deadline exceeded") -> HumanTask:
        task = self.get_task(task_id)
        task.status = TaskStatus.ESCALATED
        task.priority = TaskPriority.CRITICAL
        logger.warning(f"[HUMAN TASK MANAGER] Task '{task_id}' ESCALATED: {escalation_reason}")
        return task

    def get_task(self, task_id: str) -> HumanTask:
        task = self._tasks.get(task_id)
        if not task:
            raise TaskAssignmentException(task_id, "Task not found")
        return task

    def list_tasks(self, tenant_id: Optional[str] = None, assigned_user_id: Optional[str] = None) -> List[HumanTask]:
        res = list(self._tasks.values())
        if tenant_id:
            res = [r for r in res if r.tenant_id == tenant_id]
        if assigned_user_id:
            res = [r for r in res if r.assigned_user_id == assigned_user_id]
        return res
