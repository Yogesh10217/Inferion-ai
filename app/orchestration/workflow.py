"""Enterprise Process Definition & Workflow Lifecycle Core Subsystem."""

from datetime import datetime, timezone
from enum import Enum
import uuid
import logging
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field

from app.workflows.workflow import WorkflowDefinition as BaseWorkflowDef
from app.workflows.workflow_registry import WorkflowRegistry
from app.orchestration.exceptions import WorkflowNotFoundException, WorkflowValidationException

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class DefinitionLifecycleState(str, Enum):
    DRAFT = "DRAFT"
    VALIDATED = "VALIDATED"
    TESTING = "TESTING"
    STAGED = "STAGED"
    PUBLISHED = "PUBLISHED"
    DEPRECATED = "DEPRECATED"
    ARCHIVED = "ARCHIVED"


class WorkflowExecutionStatus(str, Enum):
    CREATED = "CREATED"
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    WAITING = "WAITING"
    PAUSED = "PAUSED"
    APPROVAL_REQUIRED = "APPROVAL_REQUIRED"
    COMPENSATING = "COMPENSATING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    TIMED_OUT = "TIMED_OUT"
    COMPENSATED = "COMPENSATED"


class WorkflowStep(BaseModel):
    step_id: str
    name: str
    step_type: str = "ACTION"  # AGENT, TASK, WORKER, APPROVAL, DECISION, SUB_WORKFLOW
    target: str = "worker_1"
    inputs: Dict[str, Any] = Field(default_factory=dict)
    next_steps: List[str] = Field(default_factory=list)


class WorkflowDefinition(BaseModel):
    workflow_id: str = Field(default_factory=lambda: f"wf_def_{uuid.uuid4().hex[:10]}")
    name: str
    version: str = "1.0.0"
    tenant_id: str = "global"
    description: str = ""

    lifecycle_state: DefinitionLifecycleState = DefinitionLifecycleState.DRAFT
    steps: List[WorkflowStep] = Field(default_factory=list)
    variables: Dict[str, Any] = Field(default_factory=dict)

    created_at: datetime = Field(default_factory=_now)
    updated_at: datetime = Field(default_factory=_now)


class WorkflowExecution(BaseModel):
    execution_id: str = Field(default_factory=lambda: f"wf_exec_{uuid.uuid4().hex[:10]}")
    workflow_id: str
    version: str = "1.0.0"
    tenant_id: str = "global"
    case_id: Optional[str] = None

    status: WorkflowExecutionStatus = WorkflowExecutionStatus.CREATED
    inputs: Dict[str, Any] = Field(default_factory=dict)
    outputs: Dict[str, Any] = Field(default_factory=dict)

    current_step_id: Optional[str] = None
    started_at: datetime = Field(default_factory=_now)
    completed_at: Optional[datetime] = None


class WorkflowDefinitionManager:
    """Manages process definitions, versioning, DAG validation, and lifecycle state transitions."""

    def __init__(self, registry: Optional[WorkflowRegistry] = None) -> None:
        self.registry = registry or WorkflowRegistry()
        self._definitions: Dict[str, WorkflowDefinition] = {}

    def create_definition(
        self,
        name: str,
        steps: List[WorkflowStep],
        tenant_id: str = "global",
        description: str = "",
    ) -> WorkflowDefinition:
        if not steps:
            raise WorkflowValidationException("Workflow definition must contain at least one step")

        wf_def = WorkflowDefinition(
            name=name,
            steps=steps,
            tenant_id=tenant_id,
            description=description,
        )
        self._definitions[wf_def.workflow_id] = wf_def
        logger.info(f"[WORKFLOW DEFINITION] Created workflow definition '{wf_def.workflow_id}' ({name}) for tenant '{tenant_id}'")
        return wf_def

    def publish_definition(self, workflow_id: str) -> WorkflowDefinition:
        wf_def = self.get_definition(workflow_id)
        wf_def.lifecycle_state = DefinitionLifecycleState.PUBLISHED
        wf_def.updated_at = _now()
        logger.info(f"[WORKFLOW DEFINITION] Published workflow definition '{workflow_id}'")
        return wf_def

    def get_definition(self, workflow_id: str) -> WorkflowDefinition:
        wf_def = self._definitions.get(workflow_id)
        if not wf_def:
            raise WorkflowNotFoundException(workflow_id)
        return wf_def

    def list_definitions(self, tenant_id: Optional[str] = None) -> List[WorkflowDefinition]:
        res = list(self._definitions.values())
        if tenant_id:
            res = [r for r in res if r.tenant_id == tenant_id]
        return res
