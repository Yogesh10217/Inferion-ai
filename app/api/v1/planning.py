"""
FastAPI Router for Autonomous Planning, Reasoning & Self-Improvement (/v1/plans)
"""

from typing import Dict, Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.learning.learning_engine import LearningEngine
from app.planning.exceptions import ResourcePlanningError
from app.planning.execution_plan import ExecutionPlan
from app.planning.governance import PlanningGovernanceEngine
from app.planning.planner import Planner
from app.planning.planning_billing import PlanningBillingTracker
from app.reasoning.reasoning_engine import ReasoningEngine
from app.simulation.simulator import ExecutionSimulator

router = APIRouter(prefix="/v1/plans", tags=["planning"])

# In-memory plan store and subsystems
_plans_store: Dict[str, ExecutionPlan] = {}
_global_planner = Planner()
_global_reasoning = ReasoningEngine()
_global_simulator = ExecutionSimulator()
_global_learning = LearningEngine()
_global_billing = PlanningBillingTracker()


class PlanCreateSchema(BaseModel):
    title: str
    description: str = ""
    tenant_id: str = "global"
    workspace_id: str = "default_workspace"


class PlanExecuteSchema(BaseModel):
    tenant_id: str = "global"
    budget_dollars: float = 50.0


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_plan(data: PlanCreateSchema):
    plan = _global_planner.create_plan(
        goal_title=data.title,
        description=data.description,
        tenant_id=data.tenant_id,
        workspace_id=data.workspace_id,
    )
    _plans_store[plan.plan_id] = plan
    _global_billing.record_usage(data.tenant_id, "planning", cost=plan.estimated_cost)
    return {"status": "created", "plan": plan.model_dump()}


@router.get("")
async def list_plans(tenant_id: str = "global"):
    plans = [p.model_dump() for p in _plans_store.values() if p.tenant_id in (tenant_id, "global", "default_tenant")]
    return {"plans": plans}


@router.get("/{id}")
async def get_plan(id: str):
    if id not in _plans_store:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Plan '{id}' not found")
    return {"plan": _plans_store[id].model_dump()}


@router.patch("/{id}")
async def update_plan(id: str, title: Optional[str] = None, confidence_score: Optional[float] = None):
    if id not in _plans_store:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Plan '{id}' not found")
    plan = _plans_store[id]
    if title:
        plan.title = title
    if confidence_score is not None:
        plan.confidence_score = confidence_score
    return {"status": "updated", "plan_id": id}


@router.delete("/{id}")
async def delete_plan(id: str):
    if id not in _plans_store:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Plan '{id}' not found")
    del _plans_store[id]
    return {"status": "deleted", "plan_id": id}


@router.post("/{id}/simulate")
async def simulate_plan(id: str):
    if id not in _plans_store:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Plan '{id}' not found")
    plan = _plans_store[id]
    sim_res = _global_simulator.simulate_plan(plan)
    _global_billing.record_usage(plan.tenant_id, "simulation", cost=0.002)
    return {"simulation": sim_res}


@router.post("/{id}/execute")
async def execute_plan(id: str, data: PlanExecuteSchema):
    if id not in _plans_store:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Plan '{id}' not found")
    plan = _plans_store[id]
    try:
        PlanningGovernanceEngine.validate_plan_execution(plan, tenant_id=data.tenant_id, workspace_budget_dollars=data.budget_dollars)
    except ResourcePlanningError as rpe:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(rpe))

    plan.status = "executing"
    # Execute reasoning steps
    reason_res = _global_reasoning.reason(plan.title, strategy="chain_of_thought")
    plan.status = "completed"

    _global_billing.record_usage(data.tenant_id, "execution", cost=plan.estimated_cost)
    return {
        "status": "completed",
        "plan_id": id,
        "execution_output": reason_res,
    }


@router.post("/{id}/reflect")
async def reflect_plan(id: str):
    if id not in _plans_store:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Plan '{id}' not found")
    plan = _plans_store[id]
    trace = [{"step": i, "status": "completed"} for i, _ in enumerate(plan.tasks)]
    reflection = _global_reasoning.reflection_engine.analyze_execution(id, trace, plan.status)
    return {"reflection": reflection}


@router.post("/{id}/optimize")
async def optimize_plan(id: str):
    if id not in _plans_store:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Plan '{id}' not found")
    plan = _plans_store[id]
    opt_plan = _global_planner.optimize_plan(plan)
    _plans_store[id] = opt_plan
    _global_billing.record_usage(plan.tenant_id, "optimization", cost=0.001)
    return {"status": "optimized", "plan": opt_plan.model_dump()}


@router.get("/{id}/metrics")
async def get_plan_metrics(id: str):
    if id not in _plans_store:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Plan '{id}' not found")
    plan = _plans_store[id]
    summary = _global_billing.get_billing_summary(plan.tenant_id)
    return {"plan_id": id, "metrics": summary}


@router.get("/{id}/billing")
async def get_plan_billing(id: str):
    if id not in _plans_store:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Plan '{id}' not found")
    plan = _plans_store[id]
    summary = _global_billing.get_billing_summary(plan.tenant_id)
    return {"plan_id": id, "billing": summary}


@router.get("/{id}/history")
async def get_plan_history(id: str):
    if id not in _plans_store:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Plan '{id}' not found")
    plan = _plans_store[id]
    recs = _global_reasoning.reflection_engine.list_recommendations()
    return {"plan_id": id, "history": [r.model_dump() for r in recs]}
