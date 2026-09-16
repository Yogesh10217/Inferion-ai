"""
FastAPI Router for Digital Workers (/v1/workers)
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.workers.worker_manager import WorkerManager

router = APIRouter(prefix="/v1/workers", tags=["workers"])

_global_worker_manager = WorkerManager()


class WorkerCreateSchema(BaseModel):
    name: str
    template_type: str = "custom"
    tenant_id: str = "global"
    workspace_id: str = "default_workspace"


class WorkerGoalSchema(BaseModel):
    goal: str


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_worker(data: WorkerCreateSchema):
    worker = _global_worker_manager.create_worker(
        name=data.name,
        template_type=data.template_type,
        tenant_id=data.tenant_id,
        workspace_id=data.workspace_id,
    )
    return {"status": "created", "worker": worker.model_dump()}


@router.get("")
async def list_workers(tenant_id: str = "global"):
    workers = _global_worker_manager.list_workers(tenant_id=tenant_id)
    return {"workers": [w.model_dump() for w in workers]}


@router.get("/{id}")
async def get_worker(id: str):
    w = _global_worker_manager.get_worker(id)
    if not w:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Worker '{id}' not found")
    return {"worker": w.model_dump()}


@router.delete("/{id}")
async def delete_worker(id: str):
    ok = _global_worker_manager.terminate_worker(id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Worker '{id}' not found")
    return {"status": "terminated", "worker_id": id}


@router.post("/{id}/goal")
async def assign_worker_goal(id: str, data: WorkerGoalSchema):
    try:
        res = await _global_worker_manager.assign_goal(id, data.goal)
        return {"status": "executed", "result": res}
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ve))


@router.post("/{id}/pause")
async def pause_worker(id: str):
    w = _global_worker_manager.get_worker(id)
    if not w:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Worker '{id}' not found")
    w.status = "paused"
    return {"status": "paused", "worker_id": id}


@router.post("/{id}/resume")
async def resume_worker(id: str):
    w = _global_worker_manager.get_worker(id)
    if not w:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Worker '{id}' not found")
    w.status = "idle"
    return {"status": "idle", "worker_id": id}


@router.post("/{id}/terminate")
async def terminate_worker(id: str):
    return await delete_worker(id)
