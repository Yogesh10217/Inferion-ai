"""
Autonomous Execution Subsystem Package
"""

from app.autonomy.exceptions import AutonomyException, ExecutionEngineError, CheckpointError, ApprovalRequiredException, EmergencyStopException
from app.autonomy.state_machine import ExecutionStateMachine, ExecutionState
from app.autonomy.task_scheduler import TaskScheduler, ScheduledTask
from app.autonomy.event_engine import EventEngine, AutonomyEvent, AutonomyEventType
from app.autonomy.checkpoint_manager import CheckpointManager, ExecutionSnapshot
from app.autonomy.execution_governance import ExecutionGovernanceEngine
from app.autonomy.execution_audit import ExecutionAuditLogger, AuditEntry
from app.autonomy.execution_metrics import (
    autonomous_runs_total,
    autonomous_runs_active,
    autonomous_runs_failed,
    autonomous_runs_completed,
    autonomous_execution_duration_seconds,
    autonomous_checkpoints_total,
    autonomous_recoveries_total,
    autonomous_cost_total,
)
from app.autonomy.execution_engine import AutonomousExecutionEngine

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
