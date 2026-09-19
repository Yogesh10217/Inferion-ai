"""Execution Lifecycle Management Subsystem (Phase 5.36)."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.agent_orchestration.delegation import AgentDelegationManager
from app.agent_orchestration.exceptions import (
    AgentExecutionNotFoundException,
    CrossTenantAgentAccessException,
)
from app.platform_contracts.delegation import DelegationRequest, DelegationTarget
from app.platform_contracts.tenant import TenantAccessGuard


class AgentExecutionStatus(str, Enum):
    PENDING = "PENDING"
    AUTHORIZED = "AUTHORIZED"
    EXECUTING = "EXECUTING"
    DELEGATED = "DELEGATED"
    VERIFYING = "VERIFYING"
    COMPLETED = "COMPLETED"
    BLOCKED = "BLOCKED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class AgentExecutionStep(BaseModel):
    step_id: str = Field(default_factory=lambda: f"execstep_{uuid.uuid4().hex[:10]}")
    step_number: int
    action: str
    target_system: DelegationTarget = DelegationTarget.PLATFORM_OPERATIONS
    delegation_id: Optional[str] = None
    status: str = "PENDING"
    output: Dict[str, Any] = Field(default_factory=dict)
    executed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ExecutionResult(BaseModel):
    execution_id: str
    status: AgentExecutionStatus
    delegation_results: List[Dict[str, Any]] = Field(default_factory=list)
    output_summary: str = ""
    error: Optional[str] = None


class ExecutionFailure(BaseModel):
    failure_id: str = Field(default_factory=lambda: f"fail_{uuid.uuid4().hex[:10]}")
    failure_type: str
    error_message: str
    is_recoverable: bool = True


class ExecutionVerification(BaseModel):
    verification_id: str = Field(default_factory=lambda: f"ver_{uuid.uuid4().hex[:10]}")
    is_verified: bool = True
    details: str = "Delegated execution confirmed by platform verification engine."


class AgentExecution(BaseModel):
    execution_id: str = Field(default_factory=lambda: f"exec_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    agent_id: str
    task_id: str
    plan_id: str
    status: AgentExecutionStatus = AgentExecutionStatus.PENDING
    execution_steps: List[AgentExecutionStep] = Field(default_factory=list)
    delegation_requests: List[DelegationRequest] = Field(default_factory=list)
    trace_id: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AgentExecutionManager:
    """Manages execution sessions strictly by creating and processing governed DelegationRequests."""

    def __init__(
        self,
        delegation_manager: Optional[AgentDelegationManager] = None,
        tenant_guard: Optional[TenantAccessGuard] = None,
    ) -> None:
        self.delegation_manager = delegation_manager or AgentDelegationManager()
        self.tenant_guard = tenant_guard or TenantAccessGuard()
        self._executions: Dict[str, AgentExecution] = {}

    def start_execution(
        self,
        tenant_id: str,
        agent_id: str,
        task_id: str,
        plan_id: str,
        actions: List[Dict[str, Any]],
        execution_id: Optional[str] = None,
    ) -> AgentExecution:
        eid = execution_id or f"exec_{uuid.uuid4().hex[:12]}"

        steps = []
        delegations = []

        for idx, act in enumerate(actions, start=1):
            target_str = act.get("target_system", "PLATFORM_OPERATIONS")
            try:
                target_enum = DelegationTarget[target_str]
            except Exception:
                target_enum = DelegationTarget.PLATFORM_OPERATIONS

            del_req = self.delegation_manager.create_delegation_request(
                tenant_id=tenant_id,
                target=target_enum,
                action=act.get("action", "execute"),
                payload=act.get("parameters", {}),
            )
            delegations.append(del_req)

            steps.append(
                AgentExecutionStep(
                    step_number=idx,
                    action=act.get("action", "execute"),
                    target_system=target_enum,
                    delegation_id=del_req.delegation_id,
                    status="DELEGATED",
                )
            )

        execution = AgentExecution(
            execution_id=eid,
            tenant_id=tenant_id,
            agent_id=agent_id,
            task_id=task_id,
            plan_id=plan_id,
            status=AgentExecutionStatus.DELEGATED,
            execution_steps=steps,
            delegation_requests=delegations,
        )
        self._executions[execution.execution_id] = execution
        return execution

    def get_execution(self, execution_id: str, tenant_id: str) -> AgentExecution:
        execution = self._executions.get(execution_id)
        if not execution:
            raise AgentExecutionNotFoundException(execution_id)

        try:
            self.tenant_guard.enforce_isolation(tenant_id, execution.tenant_id)
        except Exception:
            raise CrossTenantAgentAccessException(tenant_id, execution.tenant_id)

        return execution

    def complete_execution(self, execution_id: str, tenant_id: str) -> AgentExecution:
        execution = self.get_execution(execution_id, tenant_id)
        for s in execution.execution_steps:
            s.status = "COMPLETED"
            if s.delegation_id:
                self.delegation_manager.simulate_delegated_execution(s.delegation_id, tenant_id)
        execution.status = AgentExecutionStatus.COMPLETED
        execution.updated_at = datetime.now(timezone.utc)
        return execution
