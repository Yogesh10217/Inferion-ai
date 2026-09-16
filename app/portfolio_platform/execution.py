"""Delegation-Only Initiative Execution Subsystem."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, Optional

from pydantic import BaseModel, Field

from app.portfolio_platform.exceptions import PortfolioPolicyViolationException


class ExecutionTarget(str, Enum):
    APPLICATION_PLATFORM = "APPLICATION_PLATFORM"
    DEVELOPER_PLATFORM = "DEVELOPER_PLATFORM"
    ORCHESTRATION = "ORCHESTRATION"
    PLATFORM_OPERATIONS = "PLATFORM_OPERATIONS"
    INTEGRATION = "INTEGRATION"


class ExecutionStatus(str, Enum):
    PLANNED = "PLANNED"
    DELEGATED = "DELEGATED"
    EXECUTING = "EXECUTING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class InitiativeExecutionPlan(BaseModel):
    execution_plan_id: str = Field(default_factory=lambda: f"execplan_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    initiative_id: str
    target: ExecutionTarget = ExecutionTarget.APPLICATION_PLATFORM
    status: ExecutionStatus = ExecutionStatus.PLANNED
    delegated_reference_id: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class PortfolioExecutionManager:
    """Manages delegation of approved initiatives to existing execution platforms."""

    def __init__(self) -> None:
        self._plans: Dict[str, InitiativeExecutionPlan] = {}

    def create_execution_plan(
        self,
        tenant_id: str,
        initiative_id: str,
        target: ExecutionTarget = ExecutionTarget.APPLICATION_PLATFORM,
    ) -> InitiativeExecutionPlan:
        plan = InitiativeExecutionPlan(
            tenant_id=tenant_id,
            initiative_id=initiative_id,
            target=target,
        )
        self._plans[plan.execution_plan_id] = plan
        return plan

    def delegate_execution(
        self,
        execution_plan_id: str,
        tenant_id: str,
        target_manager_name: str = "ApplicationPlatformManager",
    ) -> InitiativeExecutionPlan:
        plan = self._plans.get(execution_plan_id)
        if not plan or plan.tenant_id != tenant_id:
            raise PortfolioPolicyViolationException(f"Execution plan '{execution_plan_id}' not found for tenant '{tenant_id}'.")

        plan.status = ExecutionStatus.DELEGATED
        plan.delegated_reference_id = f"delegated_{target_manager_name}_{uuid.uuid4().hex[:8]}"
        plan.status = ExecutionStatus.COMPLETED
        return plan
