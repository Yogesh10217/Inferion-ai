"""
FastAPI Router for Autonomous Execution Engine (/v1/autonomy)
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.autonomy.exceptions import AutonomyException, EmergencyStopException
from app.autonomy.execution_engine import AutonomousExecutionEngine

router = APIRouter(prefix="/autonomy", tags=["autonomy"])

_global_autonomy = AutonomousExecutionEngine()


class GoalRunSchema(BaseModel):
    goal: str
    tenant_id: str = "global"
    workspace_id: str = "default_workspace"


@router.post("/goals", status_code=status.HTTP_201_CREATED)
async def submit_goal(data: GoalRunSchema):
    try:
        res = await _global_autonomy.execute_goal(data.goal, tenant_id=data.tenant_id, workspace_id=data.workspace_id)
        return {"status": "submitted", "execution": res}
    except EmergencyStopException as ese:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(ese))
    except AutonomyException as ae:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(ae))


@router.post("/run")
async def run_goal(data: GoalRunSchema):
    return await submit_goal(data)


@router.post("/pause")
async def pause_execution(execution_id: str):
    st = _global_autonomy.pause_execution(execution_id)
    return {"execution_id": execution_id, "status": st}


@router.post("/resume")
async def resume_execution(execution_id: str):
    st = _global_autonomy.resume_execution(execution_id)
    return {"execution_id": execution_id, "status": st}


@router.post("/stop")
async def stop_execution(execution_id: str):
    st = _global_autonomy.stop_execution(execution_id)
    return {"execution_id": execution_id, "status": st}


@router.get("/executions")
async def list_executions():
    sms = _global_autonomy.active_state_machines
    return {"executions": [{"execution_id": k, "status": v.current_state.value} for k, v in sms.items()]}


@router.get("/executions/{id}")
async def get_execution(id: str):
    sm = _global_autonomy.active_state_machines.get(id)
    if not sm:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Execution '{id}' not found")
    chk = _global_autonomy.checkpoint_mgr.get_latest_checkpoint(id)
    return {"execution_id": id, "status": sm.current_state.value, "checkpoint": chk.model_dump() if chk else None}


@router.get("/metrics")
async def get_metrics():
    return {"status": "active", "total_state_machines": len(_global_autonomy.active_state_machines)}
