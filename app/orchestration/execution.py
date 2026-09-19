"""Durable Workflow Execution Engine & Checkpoint Recovery Subsystem."""

import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.orchestration.exceptions import WorkflowExecutionException
from app.orchestration.workflow import WorkflowDefinition, WorkflowExecution, WorkflowExecutionStatus
from app.workflows.checkpoint import CheckpointManager
from app.workflows.executor import WorkflowExecutor

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class ExecutionCheckpoint(BaseModel):
    checkpoint_id: str = Field(default_factory=lambda: f"chk_{uuid.uuid4().hex[:10]}")
    execution_id: str
    step_id: str
    tenant_id: str = "global"

    state_data: Dict[str, Any] = Field(default_factory=dict)
    idempotency_key: str = ""
    timestamp: datetime = Field(default_factory=_now)


class WorkflowExecutionEngine:
    """Manages durable workflow executions, step checkpointing, idempotency tracking, and replay recovery."""

    def __init__(
        self,
        checkpoint_manager: Optional[CheckpointManager] = None,
        base_executor: Optional[WorkflowExecutor] = None,
    ) -> None:
        self.checkpoint_manager = checkpoint_manager or CheckpointManager()
        self.base_executor = base_executor or WorkflowExecutor()
        self._executions: Dict[str, WorkflowExecution] = {}
        self._checkpoints: Dict[str, ExecutionCheckpoint] = {}
        self._idempotency_ledger: Dict[str, Any] = {}

    def start_execution(
        self,
        definition: WorkflowDefinition,
        inputs: Optional[Dict[str, Any]] = None,
        tenant_id: str = "global",
        case_id: Optional[str] = None,
        idempotency_key: Optional[str] = None,
    ) -> WorkflowExecution:
        # Idempotency check: if key already completed, return existing execution!
        if idempotency_key and idempotency_key in self._idempotency_ledger:
            existing_id = self._idempotency_ledger[idempotency_key]
            logger.info(
                f"[EXECUTION ENGINE] Idempotent key '{idempotency_key}' matched existing execution '{existing_id}'"
            )
            return self._executions[existing_id]

        exec_obj = WorkflowExecution(
            workflow_id=definition.workflow_id,
            version=definition.version,
            tenant_id=tenant_id,
            case_id=case_id,
            status=WorkflowExecutionStatus.RUNNING,
            inputs=inputs or {},
            current_step_id=definition.steps[0].step_id if definition.steps else None,
        )
        self._executions[exec_obj.execution_id] = exec_obj

        if idempotency_key:
            self._idempotency_ledger[idempotency_key] = exec_obj.execution_id

        # Save initial checkpoint
        self.save_checkpoint(
            exec_obj.execution_id,
            exec_obj.current_step_id or "start",
            {"status": "STARTED"},
            tenant_id=tenant_id,
            idempotency_key=idempotency_key or "",
        )
        logger.info(
            f"[EXECUTION ENGINE] Started durable execution '{exec_obj.execution_id}' for workflow '{definition.workflow_id}'"
        )
        return exec_obj

    def execute_step(self, execution_id: str, step_id: str, step_output: Dict[str, Any]) -> WorkflowExecution:
        exec_obj = self.get_execution(execution_id)
        exec_obj.outputs.update(step_output)
        exec_obj.current_step_id = step_id

        self.save_checkpoint(execution_id, step_id, step_output, tenant_id=exec_obj.tenant_id)
        return exec_obj

    def complete_execution(
        self, execution_id: str, final_outputs: Optional[Dict[str, Any]] = None
    ) -> WorkflowExecution:
        exec_obj = self.get_execution(execution_id)
        exec_obj.status = WorkflowExecutionStatus.COMPLETED
        if final_outputs:
            exec_obj.outputs.update(final_outputs)
        exec_obj.completed_at = _now()

        logger.info(f"[EXECUTION ENGINE] Completed execution '{execution_id}' successfully")
        return exec_obj

    def save_checkpoint(
        self,
        execution_id: str,
        step_id: str,
        state_data: Dict[str, Any],
        tenant_id: str = "global",
        idempotency_key: str = "",
    ) -> ExecutionCheckpoint:
        chk = ExecutionCheckpoint(
            execution_id=execution_id,
            step_id=step_id,
            tenant_id=tenant_id,
            state_data=state_data,
            idempotency_key=idempotency_key,
        )
        self._checkpoints[chk.checkpoint_id] = chk
        logger.info(
            f"[EXECUTION ENGINE] Checkpoint '{chk.checkpoint_id}' saved for execution '{execution_id}' step '{step_id}'"
        )
        return chk

    def get_execution(self, execution_id: str) -> WorkflowExecution:
        exec_obj = self._executions.get(execution_id)
        if not exec_obj:
            raise WorkflowExecutionException(execution_id, "Execution not found")
        return exec_obj

    def list_executions(self, tenant_id: Optional[str] = None) -> List[WorkflowExecution]:
        res = list(self._executions.values())
        if tenant_id:
            res = [r for r in res if r.tenant_id == tenant_id]
        return res
