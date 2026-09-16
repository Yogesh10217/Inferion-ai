"""
Autonomous Execution Subsystem Package
"""

from app.autonomy.checkpoint_manager import CheckpointManager, ExecutionSnapshot
from app.autonomy.event_engine import AutonomyEvent, AutonomyEventType, EventEngine
from app.autonomy.exceptions import (
    ApprovalRequiredException,
    AutonomyException,
    CheckpointError,
    EmergencyStopException,
    ExecutionEngineError,
)
from app.autonomy.execution_audit import AuditEntry, ExecutionAuditLogger
from app.autonomy.execution_engine import AutonomousExecutionEngine
from app.autonomy.execution_governance import ExecutionGovernanceEngine
from app.autonomy.state_machine import ExecutionState, ExecutionStateMachine
from app.autonomy.task_scheduler import ScheduledTask, TaskScheduler

__all__ = [
    "AutonomyException",
    "ExecutionEngineError",
    "CheckpointError",
    "ApprovalRequiredException",
    "EmergencyStopException",
    "ExecutionStateMachine",
    "ExecutionState",
    "TaskScheduler",
    "ScheduledTask",
    "EventEngine",
    "AutonomyEvent",
    "AutonomyEventType",
    "CheckpointManager",
    "ExecutionSnapshot",
    "ExecutionGovernanceEngine",
    "ExecutionAuditLogger",
    "AuditEntry",
    "AutonomousExecutionEngine",
]
