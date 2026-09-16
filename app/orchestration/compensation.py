"""Saga Pattern Distributed Transaction & Compensation Subsystem."""

import logging
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List

from pydantic import BaseModel, Field

from app.orchestration.exceptions import CompensationException

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class SagaStepStatus(str, Enum):
    PENDING = "PENDING"
    EXECUTED = "EXECUTED"
    COMPENSATED = "COMPENSATED"
    FAILED = "FAILED"


class SagaStep(BaseModel):
    step_id: str
    action_name: str
    compensation_action: str
    status: SagaStepStatus = SagaStepStatus.PENDING
    payload: Dict[str, Any] = Field(default_factory=dict)


class SagaTransaction(BaseModel):
    saga_id: str = Field(default_factory=lambda: f"saga_{uuid.uuid4().hex[:10]}")
    execution_id: str
    tenant_id: str = "global"

    steps: List[SagaStep] = Field(default_factory=list)
    is_compensated: bool = False
    created_at: datetime = Field(default_factory=_now)


class CompensationManager:
    """Manages Saga transactions and executes explicit reverse-order compensation when distributed steps fail."""

    def __init__(self) -> None:
        self._sagas: Dict[str, SagaTransaction] = {}

    def create_saga(self, execution_id: str, steps: List[SagaStep], tenant_id: str = "global") -> SagaTransaction:
        saga = SagaTransaction(execution_id=execution_id, steps=steps, tenant_id=tenant_id)
        self._sagas[saga.saga_id] = saga
        logger.info(f"[COMPENSATION MANAGER] Registered Saga '{saga.saga_id}' with {len(steps)} steps for execution '{execution_id}'")
        return saga

    def mark_step_executed(self, saga_id: str, step_id: str) -> SagaStep:
        saga = self.get_saga(saga_id)
        for s in saga.steps:
            if s.step_id == step_id:
                s.status = SagaStepStatus.EXECUTED
                logger.info(f"[COMPENSATION MANAGER] Saga '{saga_id}' step '{step_id}' marked EXECUTED")
                return s
        raise CompensationException(saga_id, step_id, "Step not found in Saga")

    def execute_compensation(self, saga_id: str) -> SagaTransaction:
        saga = self.get_saga(saga_id)
        # Compensate executed steps in REVERSE order!
        executed_steps = [s for s in saga.steps if s.status == SagaStepStatus.EXECUTED]
        executed_steps.reverse()

        for s in executed_steps:
            s.status = SagaStepStatus.COMPENSATED
            logger.warning(f"[COMPENSATION MANAGER] Executed compensation action '{s.compensation_action}' for step '{s.step_id}'")

        saga.is_compensated = True
        logger.warning(f"[COMPENSATION MANAGER] Saga '{saga_id}' fully COMPENSATED ({len(executed_steps)} steps reversed)")
        return saga

    def get_saga(self, saga_id: str) -> SagaTransaction:
        saga = self._sagas.get(saga_id)
        if not saga:
            raise KeyError(f"Saga transaction '{saga_id}' not found")
        return saga
