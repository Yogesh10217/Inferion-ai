"""Integration Execution Lifecycle & Delegation-Only Execution (Phase 5.40)."""

import hashlib
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.integration_intelligence.exceptions import (
    CrossTenantIntegrationAccessException,
    HighRiskIntegrationRequiresApprovalException,
    IntegrationExecutionBlockedException,
    InvalidAccessStateTransitionException,
)
from app.platform_contracts.delegation import DelegationRequest, DelegationStatus, DelegationTarget
from app.platform_contracts.idempotency import IdempotencyManager, IdempotencyStatus


class IntegrationExecutionStatus(str, Enum):
    REQUESTED = "REQUESTED"
    GOVERNANCE_EVALUATED = "GOVERNANCE_EVALUATED"
    APPROVAL_PENDING = "APPROVAL_PENDING"
    DELEGATED = "DELEGATED"
    EXECUTING = "EXECUTING"
    VERIFYING = "VERIFYING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class IntegrationExecutionResult(BaseModel):
    """Result payload returned by delegated execution."""
    execution_id: str
    status: IntegrationExecutionStatus
    delegation_id: str
    output_summary: str = ""
    sanitized_output: Dict[str, Any] = Field(default_factory=dict)
    completed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class IntegrationExecution(BaseModel):
    """Integration Execution Lifecycle Representation."""
    execution_id: str = Field(default_factory=lambda: f"exec_int_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    workflow_id: str
    idempotency_key: str
    replay_token: Optional[str] = None
    status: IntegrationExecutionStatus = IntegrationExecutionStatus.REQUESTED
    requires_approval: bool = False
    approval_id: Optional[str] = None
    delegation_request_id: Optional[str] = None
    fingerprint: str = ""
    is_finalized: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class IntegrationExecutionManager:
    """Manages integration execution lifecycle using DelegationRequest (no direct infrastructure mutation)."""

    def __init__(self) -> None:
        self._executions: Dict[str, IntegrationExecution] = {}
        self._seen_replay_tokens: set = set()
        self.idempotency_manager = IdempotencyManager()

    def request_execution(
        self,
        tenant_id: str,
        workflow_id: str,
        idempotency_key: str,
        replay_token: Optional[str] = None,
        requires_approval: bool = False,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> IntegrationExecution:
        # Replay protection check
        if replay_token and replay_token in self._seen_replay_tokens:
            raise IntegrationExecutionBlockedException(
                "N/A", f"Event replay detected with token '{replay_token}'. Action blocked."
            )
        if replay_token:
            self._seen_replay_tokens.add(replay_token)

        # Idempotency protection check
        existing_record = self.idempotency_manager.check_or_start(
            tenant_id=tenant_id,
            operation_type="INTEGRATION_EXECUTION",
            idempotency_key=idempotency_key,
            request_payload={"workflow_id": workflow_id},
        )
        if existing_record and existing_record.result_payload:
            existing_exec_id = existing_record.result_payload.get("execution_id")
            if existing_exec_id and existing_exec_id in self._executions:
                return self._executions[existing_exec_id]

        exec_obj = IntegrationExecution(
            tenant_id=tenant_id,
            workflow_id=workflow_id,
            idempotency_key=idempotency_key,
            replay_token=replay_token,
            status=IntegrationExecutionStatus.REQUESTED,
            requires_approval=requires_approval,
            metadata=metadata or {},
        )
        self._executions[exec_obj.execution_id] = exec_obj

        # Save execution in idempotency record
        self.idempotency_manager.complete_operation(
            tenant_id=tenant_id,
            operation_type="INTEGRATION_EXECUTION",
            idempotency_key=idempotency_key,
            result_payload={"execution_id": exec_obj.execution_id},
            status=IdempotencyStatus.RUNNING,
        )
        return exec_obj

    def evaluate_governance(self, tenant_id: str, execution_id: str, is_governed_clean: bool = True) -> IntegrationExecution:
        exec_obj = self.get_execution(tenant_id, execution_id)
        if exec_obj.status != IntegrationExecutionStatus.REQUESTED:
            raise InvalidAccessStateTransitionException(exec_obj.status.value, IntegrationExecutionStatus.GOVERNANCE_EVALUATED.value)

        if exec_obj.requires_approval and not exec_obj.approval_id:
            exec_obj.status = IntegrationExecutionStatus.APPROVAL_PENDING
        else:
            exec_obj.status = IntegrationExecutionStatus.GOVERNANCE_EVALUATED
        return exec_obj

    def approve_execution(self, tenant_id: str, execution_id: str, approval_id: str = "appr_int_123") -> IntegrationExecution:
        exec_obj = self.get_execution(tenant_id, execution_id)
        exec_obj.approval_id = approval_id
        exec_obj.status = IntegrationExecutionStatus.GOVERNANCE_EVALUATED
        return exec_obj

    def delegate_execution(self, tenant_id: str, execution_id: str) -> DelegationRequest:
        exec_obj = self.get_execution(tenant_id, execution_id)
        if exec_obj.requires_approval and not exec_obj.approval_id:
            raise HighRiskIntegrationRequiresApprovalException("EXECUTE_WORKFLOW", 85.0)

        del_req = DelegationRequest(
            tenant_id=tenant_id,
            target=DelegationTarget.ORCHESTRATION,
            action="EXECUTE_INTEGRATION_WORKFLOW",
            status=DelegationStatus.QUEUED,
            payload={
                "execution_id": exec_obj.execution_id,
                "workflow_id": exec_obj.workflow_id,
                "idempotency_key": exec_obj.idempotency_key,
            },
        )
        exec_obj.status = IntegrationExecutionStatus.DELEGATED
        exec_obj.delegation_request_id = del_req.delegation_id
        return del_req

    def finalize_execution(self, tenant_id: str, execution_id: str, status: IntegrationExecutionStatus = IntegrationExecutionStatus.COMPLETED) -> IntegrationExecution:
        exec_obj = self.get_execution(tenant_id, execution_id)
        exec_obj.status = status
        exec_obj.is_finalized = True
        exec_obj.completed_at = datetime.now(timezone.utc)

        raw = f"{exec_obj.execution_id}:{exec_obj.tenant_id}:{exec_obj.workflow_id}:{status.value}:{exec_obj.completed_at.isoformat()}"
        exec_obj.fingerprint = hashlib.sha256(raw.encode("utf-8")).hexdigest()

        self.idempotency_manager.complete_operation(
            tenant_id=tenant_id,
            operation_type="INTEGRATION_EXECUTION",
            idempotency_key=exec_obj.idempotency_key,
            result_payload={"execution_id": exec_obj.execution_id, "fingerprint": exec_obj.fingerprint},
            status=IdempotencyStatus.COMPLETED if status == IntegrationExecutionStatus.COMPLETED else IdempotencyStatus.FAILED,
        )
        return exec_obj

    def get_execution(self, tenant_id: str, execution_id: str) -> IntegrationExecution:
        exec_obj = self._executions.get(execution_id)
        if not exec_obj or exec_obj.tenant_id != tenant_id:
            raise CrossTenantIntegrationAccessException()
        return exec_obj

    def list_executions(self, tenant_id: str) -> List[IntegrationExecution]:
        return [e for e in self._executions.values() if e.tenant_id == tenant_id]
