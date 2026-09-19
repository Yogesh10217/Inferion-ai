"""Governed Integration Workflow Registry (Phase 5.40)."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.integration_intelligence.exceptions import (
    CrossTenantIntegrationAccessException,
    InvalidAccessStateTransitionException,
)


class WorkflowStatus(str, Enum):
    DRAFT = "DRAFT"
    VALIDATED = "VALIDATED"
    GOVERNED = "GOVERNED"
    READY = "READY"
    EXECUTING = "EXECUTING"
    VERIFYING = "VERIFYING"
    COMPLETED = "COMPLETED"


class WorkflowType(str, Enum):
    SYNC_API = "SYNC_API"
    ASYNC_EVENT = "ASYNC_EVENT"
    BULK_ETL = "BULK_ETL"
    CROSS_SYSTEM_SAGA = "CROSS_SYSTEM_SAGA"
    AUTOMATION_PIPELINE = "AUTOMATION_PIPELINE"


class WorkflowTrigger(str, Enum):
    SCHEDULED = "SCHEDULED"
    EVENT_DRIVEN = "EVENT_DRIVEN"
    API_INVOCATION = "API_INVOCATION"
    MANUAL_TRIGGER = "MANUAL_TRIGGER"


class WorkflowStep(BaseModel):
    """Step definition within an integration workflow."""

    step_id: str = Field(default_factory=lambda: f"step_{uuid.uuid4().hex[:8]}")
    name: str
    target_connector_id: str
    target_endpoint_id: str
    action_name: str
    is_high_risk: bool = False
    requires_compensation: bool = False
    compensation_action_name: Optional[str] = None


class IntegrationWorkflow(BaseModel):
    """Governed Integration Workflow Representation."""

    workflow_id: str = Field(default_factory=lambda: f"wf_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    name: str
    description: str = ""
    workflow_type: WorkflowType = WorkflowType.SYNC_API
    trigger: WorkflowTrigger = WorkflowTrigger.API_INVOCATION
    status: WorkflowStatus = WorkflowStatus.DRAFT
    steps: List[WorkflowStep] = Field(default_factory=list)
    is_finalized: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = Field(default_factory=dict)


class WorkflowManager:
    """Manages integration workflow definition lifecycle."""

    def __init__(self) -> None:
        self._workflows: Dict[str, IntegrationWorkflow] = {}

    def create_workflow(
        self,
        tenant_id: str,
        name: str,
        workflow_type: WorkflowType = WorkflowType.SYNC_API,
        trigger: WorkflowTrigger = WorkflowTrigger.API_INVOCATION,
        steps: Optional[List[WorkflowStep]] = None,
        description: str = "",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> IntegrationWorkflow:
        wf = IntegrationWorkflow(
            tenant_id=tenant_id,
            name=name,
            workflow_type=workflow_type,
            trigger=trigger,
            steps=steps or [],
            description=description,
            metadata=metadata or {},
        )
        self._workflows[wf.workflow_id] = wf
        return wf

    def validate_workflow(self, tenant_id: str, workflow_id: str) -> IntegrationWorkflow:
        wf = self.get_workflow(tenant_id, workflow_id)
        if wf.status != WorkflowStatus.DRAFT:
            raise InvalidAccessStateTransitionException(wf.status.value, WorkflowStatus.VALIDATED.value)
        wf.status = WorkflowStatus.VALIDATED
        wf.updated_at = datetime.now(timezone.utc)
        return wf

    def govern_workflow(self, tenant_id: str, workflow_id: str) -> IntegrationWorkflow:
        wf = self.get_workflow(tenant_id, workflow_id)
        if wf.status != WorkflowStatus.VALIDATED:
            raise InvalidAccessStateTransitionException(wf.status.value, WorkflowStatus.GOVERNED.value)
        wf.status = WorkflowStatus.GOVERNED
        wf.updated_at = datetime.now(timezone.utc)
        return wf

    def mark_ready(self, tenant_id: str, workflow_id: str) -> IntegrationWorkflow:
        wf = self.get_workflow(tenant_id, workflow_id)
        if wf.status != WorkflowStatus.GOVERNED:
            raise InvalidAccessStateTransitionException(wf.status.value, WorkflowStatus.READY.value)
        wf.status = WorkflowStatus.READY
        wf.updated_at = datetime.now(timezone.utc)
        return wf

    def complete_workflow(self, tenant_id: str, workflow_id: str) -> IntegrationWorkflow:
        wf = self.get_workflow(tenant_id, workflow_id)
        wf.status = WorkflowStatus.COMPLETED
        wf.is_finalized = True
        wf.updated_at = datetime.now(timezone.utc)
        return wf

    def get_workflow(self, tenant_id: str, workflow_id: str) -> IntegrationWorkflow:
        wf = self._workflows.get(workflow_id)
        if not wf or wf.tenant_id != tenant_id:
            raise CrossTenantIntegrationAccessException()
        return wf

    def list_workflows(self, tenant_id: str, status: Optional[WorkflowStatus] = None) -> List[IntegrationWorkflow]:
        results = [w for w in self._workflows.values() if w.tenant_id == tenant_id]
        if status:
            results = [w for w in results if w.status == status]
        return results
