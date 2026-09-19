"""
Enterprise Workflow Engine REST API Router (/v1/workflows)
"""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel, Field

from app.workflows.exceptions import CheckpointNotFoundError, GraphValidationError, WorkflowError
from app.workflows.workflow_manager import WorkflowManager

router = APIRouter(prefix="/v1/workflows", tags=["Workflows"])

# Shared global manager instance
_workflow_manager = WorkflowManager()


class CreateWorkflowRequest(BaseModel):
    id: Optional[str] = None
    name: str
    description: str = ""
    spec: Optional[Dict[str, Any]] = None


class RunWorkflowRequest(BaseModel):
    inputs: Dict[str, Any] = Field(default_factory=dict)


class ApprovalDecisionRequest(BaseModel):
    approved: bool
    feedback: Optional[str] = None


class RollbackRequest(BaseModel):
    checkpoint_id: Optional[str] = None


def get_tenant_context(
    x_organization_id: str = Header(default="default_org", alias="X-Organization-Id"),
    x_workspace_id: Optional[str] = Header(default="default_workspace", alias="X-Workspace-Id"),
) -> Dict[str, str]:
    return {
        "organization_id": x_organization_id,
        "workspace_id": x_workspace_id or "default_workspace",
    }


@router.post("", response_model=Dict[str, Any])
async def create_workflow(req: CreateWorkflowRequest, tenant: Dict[str, str] = Depends(get_tenant_context)):
    try:
        wf = _workflow_manager.create_workflow(
            workflow_id=req.id,
            name=req.name,
            description=req.description,
            organization_id=tenant["organization_id"],
            workspace_id=tenant["workspace_id"],
            spec=req.spec,
        )
        return {"status": "success", "workflow": wf.to_dict()}
    except GraphValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("", response_model=List[Dict[str, Any]])
async def list_workflows(tenant: Dict[str, str] = Depends(get_tenant_context)):
    workflows = _workflow_manager.list_workflows(organization_id=tenant["organization_id"])
    return [wf.to_dict() for wf in workflows]


@router.get("/templates", response_model=List[Dict[str, Any]])
async def list_templates():
    return _workflow_manager.get_templates()


@router.get("/{workflow_id}", response_model=Dict[str, Any])
async def get_workflow(workflow_id: str):
    try:
        wf = _workflow_manager.get_workflow(workflow_id)
        return {"workflow": wf.to_dict()}
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{workflow_id}", response_model=Dict[str, Any])
async def delete_workflow(workflow_id: str):
    _workflow_manager.delete_workflow(workflow_id)
    return {"status": "success", "message": f"Workflow '{workflow_id}' deleted"}


@router.post("/{workflow_id}/run", response_model=Dict[str, Any])
async def run_workflow(
    workflow_id: str,
    req: RunWorkflowRequest,
    tenant: Dict[str, str] = Depends(get_tenant_context),
):
    try:
        result = await _workflow_manager.run_workflow(
            workflow_id=workflow_id,
            inputs=req.inputs,
            organization_id=tenant["organization_id"],
            workspace_id=tenant["workspace_id"],
        )
        return {"status": "success", "execution": result}
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except WorkflowError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{run_id}/resume", response_model=Dict[str, Any])
async def resume_workflow(
    run_id: str,
    approval: Optional[ApprovalDecisionRequest] = None,
):
    try:
        approval_dec = {"approved": approval.approved, "feedback": approval.feedback} if approval else None
        result = await _workflow_manager.resume_workflow(run_id=run_id, approval_decision=approval_dec)
        return {"status": "success", "execution": result}
    except CheckpointNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{run_id}/approve", response_model=Dict[str, Any])
async def approve_workflow(
    run_id: str,
    decision: ApprovalDecisionRequest,
):
    req = _workflow_manager.approval_manager.get_pending_request_for_run(run_id)
    if not req:
        raise HTTPException(status_code=404, detail=f"No pending approval for run '{run_id}'")

    if decision.approved:
        _workflow_manager.approval_manager.approve(req.request_id, feedback=decision.feedback)
    else:
        _workflow_manager.approval_manager.reject(req.request_id, feedback=decision.feedback)

    res = await _workflow_manager.resume_workflow(
        run_id=run_id, approval_decision={"approved": decision.approved, "feedback": decision.feedback}
    )
    return {"status": "success", "approval": req.to_dict(), "execution": res}


@router.get("/{run_id}/history", response_model=Dict[str, Any])
async def get_workflow_history(run_id: str):
    try:
        return _workflow_manager.get_run_history(run_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{run_id}/checkpoints", response_model=List[Dict[str, Any]])
async def get_workflow_checkpoints(run_id: str):
    return _workflow_manager.get_checkpoints(run_id)


@router.post("/{run_id}/rollback", response_model=Dict[str, Any])
async def rollback_workflow(
    run_id: str,
    req: Optional[RollbackRequest] = None,
):
    try:
        chk_id = req.checkpoint_id if req else None
        return _workflow_manager.rollback(run_id, chk_id)
    except CheckpointNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{run_id}/fork", response_model=Dict[str, Any])
async def fork_workflow(
    run_id: str,
    req: Optional[RollbackRequest] = None,
):
    try:
        chk_id = req.checkpoint_id if req else None
        return _workflow_manager.fork(run_id, chk_id)
    except CheckpointNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
