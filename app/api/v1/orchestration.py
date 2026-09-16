"""FastAPI REST API Router for Phase 5.18 Enterprise Orchestration Platform."""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from app.orchestration.case_management import CasePriority, CaseType
from app.orchestration.human_tasks import TaskPriority
from app.orchestration.manager import OrchestrationManager
from app.orchestration.workflow import WorkflowStep

router = APIRouter(prefix="/v1/orchestration", tags=["Orchestration Platform"])

_global_orchestration = OrchestrationManager()


def get_orchestration_manager() -> OrchestrationManager:
    return _global_orchestration


class CreateWorkflowRequest(BaseModel):
    name: str
    steps: List[WorkflowStep]
    tenant_id: str = "global"
    description: str = ""


class StartExecutionRequest(BaseModel):
    workflow_id: str
    inputs: Dict[str, Any] = Field(default_factory=dict)
    tenant_id: str = "global"
    case_id: Optional[str] = None
    idempotency_key: Optional[str] = None


class CreateTaskRequest(BaseModel):
    title: str
    assigned_user_id: Optional[str] = None
    assigned_role: Optional[str] = None
    tenant_id: str = "global"
    case_id: Optional[str] = None
    priority: TaskPriority = TaskPriority.MEDIUM


class CreateCaseRequest(BaseModel):
    title: str
    case_type: CaseType = CaseType.CUSTOMER_ONBOARDING
    tenant_id: str = "global"
    priority: CasePriority = CasePriority.MEDIUM


class EvaluateDecisionRequest(BaseModel):
    table_id: str
    inputs: Dict[str, Any] = Field(default_factory=dict)
    tenant_id: str = "global"


@router.get("/health", status_code=status.HTTP_200_OK)
def orchestration_health():
    return {"status": "HEALTHY", "subsystem": "Enterprise Orchestration Platform", "phase": "5.18"}


@router.post("/workflows", status_code=status.HTTP_201_CREATED)
def create_workflow(
    req: CreateWorkflowRequest,
    mgr: OrchestrationManager = Depends(get_orchestration_manager),
):
    wf = mgr.definition_manager.create_definition(
        name=req.name,
        steps=req.steps,
        tenant_id=req.tenant_id,
        description=req.description,
    )
    return wf.model_dump()


@router.get("/workflows", status_code=status.HTTP_200_OK)
def list_workflows(
    tenant_id: Optional[str] = Query(None),
    mgr: OrchestrationManager = Depends(get_orchestration_manager),
):
    return {"workflows": [w.model_dump() for w in mgr.definition_manager.list_definitions(tenant_id)]}


@router.post("/workflows/{workflow_id}/publish", status_code=status.HTTP_200_OK)
def publish_workflow(
    workflow_id: str,
    mgr: OrchestrationManager = Depends(get_orchestration_manager),
):
    try:
        wf = mgr.definition_manager.publish_definition(workflow_id)
        return wf.model_dump()
    except KeyError:
        raise HTTPException(status_code=404, detail="Workflow not found")


@router.post("/executions/start", status_code=status.HTTP_200_OK)
def start_execution(
    req: StartExecutionRequest,
    mgr: OrchestrationManager = Depends(get_orchestration_manager),
):
    try:
        wf_def = mgr.definition_manager.get_definition(req.workflow_id)
        exec_obj = mgr.execution_engine.start_execution(
            definition=wf_def,
            inputs=req.inputs,
            tenant_id=req.tenant_id,
            case_id=req.case_id,
            idempotency_key=req.idempotency_key,
        )
        mgr.metrics_collector.record_execution(req.tenant_id, exec_obj.status.value)
        return exec_obj.model_dump()
    except KeyError:
        raise HTTPException(status_code=404, detail="Workflow definition not found")


@router.get("/executions", status_code=status.HTTP_200_OK)
def list_executions(
    tenant_id: Optional[str] = Query(None),
    mgr: OrchestrationManager = Depends(get_orchestration_manager),
):
    return {"executions": [e.model_dump() for e in mgr.execution_engine.list_executions(tenant_id)]}


@router.post("/tasks", status_code=status.HTTP_201_CREATED)
def create_human_task(
    req: CreateTaskRequest,
    mgr: OrchestrationManager = Depends(get_orchestration_manager),
):
    task = mgr.human_task_manager.create_task(
        title=req.title,
        assigned_user_id=req.assigned_user_id,
        assigned_role=req.assigned_role,
        tenant_id=req.tenant_id,
        case_id=req.case_id,
        priority=req.priority,
    )
    return task.model_dump()


@router.get("/tasks", status_code=status.HTTP_200_OK)
def list_human_tasks(
    tenant_id: Optional[str] = Query(None),
    assigned_user_id: Optional[str] = Query(None),
    mgr: OrchestrationManager = Depends(get_orchestration_manager),
):
    return {"tasks": [t.model_dump() for t in mgr.human_task_manager.list_tasks(tenant_id, assigned_user_id)]}


@router.post("/cases", status_code=status.HTTP_201_CREATED)
def create_case(
    req: CreateCaseRequest,
    mgr: OrchestrationManager = Depends(get_orchestration_manager),
):
    case = mgr.case_manager.create_case(
        title=req.title,
        case_type=req.case_type,
        tenant_id=req.tenant_id,
        priority=req.priority,
    )
    return case.model_dump()


@router.get("/cases", status_code=status.HTTP_200_OK)
def list_cases(
    tenant_id: Optional[str] = Query(None),
    mgr: OrchestrationManager = Depends(get_orchestration_manager),
):
    return {"cases": [c.model_dump() for c in mgr.case_manager.list_cases(tenant_id)]}


@router.get("/analytics", status_code=status.HTTP_200_OK)
def get_analytics(
    tenant_id: str = Query("global"),
    mgr: OrchestrationManager = Depends(get_orchestration_manager),
):
    insight = mgr.process_analytics_engine.generate_insight(tenant_id)
    return insight.model_dump()
