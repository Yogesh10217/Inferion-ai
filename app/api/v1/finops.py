"""FastAPI Router for FinOps & Financial Intelligence Platform (/v1/finops/*)."""

from decimal import Decimal
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field

from app.finops.manager import FinOpsManager
from app.finops.budgets import BudgetScope, BudgetPeriod, BudgetAction
from app.finops.cost_ledger import CostCategory
from app.finops.exceptions import FinOpsException

router = APIRouter(prefix="/v1/finops", tags=["finops"])

_global_finops_manager = FinOpsManager()


def get_finops() -> FinOpsManager:
    return _global_finops_manager


# Schemas
class CreateBudgetSchema(BaseModel):
    name: str
    limit_amount: Decimal
    tenant_id: str = "global"
    scope: BudgetScope = BudgetScope.TENANT
    period: BudgetPeriod = BudgetPeriod.MONTHLY
    enforcement_action: BudgetAction = BudgetAction.WARN


class EvaluateExecutionSchema(BaseModel):
    tenant_id: str = "global"
    projected_cost: Decimal = Field(default=Decimal("0.01"))


# 1. Costs & Analytics Endpoints
@router.get("/costs")
async def list_costs(tenant_id: Optional[str] = None, component: Optional[str] = None, mgr: FinOpsManager = Depends(get_finops)):
    entries = mgr.cost_ledger.list_entries(tenant_id=tenant_id, component=component)
    total = mgr.cost_ledger.get_total_cost(tenant_id=tenant_id)
    return {"total_cost": str(total), "entries": [e.model_dump() for e in entries]}


@router.get("/costs/breakdown")
async def get_cost_breakdown(tenant_id: str = "global", mgr: FinOpsManager = Depends(get_finops)):
    report = mgr.analytics_engine.generate_report(tenant_id=tenant_id)
    return {"report": report.model_dump()}


# 2. Budgets Endpoints
@router.post("/budgets", status_code=status.HTTP_201_CREATED)
async def create_budget(data: CreateBudgetSchema, mgr: FinOpsManager = Depends(get_finops)):
    b = mgr.budget_manager.create_budget(
        name=data.name,
        limit_amount=data.limit_amount,
        tenant_id=data.tenant_id,
        scope=data.scope,
        period=data.period,
        enforcement_action=data.enforcement_action,
    )
    return {"status": "created", "budget": b.model_dump()}


@router.get("/budgets")
async def list_budgets(tenant_id: Optional[str] = None, mgr: FinOpsManager = Depends(get_finops)):
    budgets = mgr.budget_manager.list_budgets(tenant_id=tenant_id)
    return {"budgets": [b.model_dump() for b in budgets]}


@router.get("/budgets/{id}")
async def get_budget(id: str, mgr: FinOpsManager = Depends(get_finops)):
    try:
        b = mgr.budget_manager.get_budget(id)
        return {"budget": b.model_dump()}
    except FinOpsException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("/budgets/evaluate")
async def evaluate_budget_execution(data: EvaluateExecutionSchema, mgr: FinOpsManager = Depends(get_finops)):
    decision = mgr.budget_manager.evaluate_execution(tenant_id=data.tenant_id, projected_cost=data.projected_cost)
    return {"decision": decision.model_dump()}


# 3. Forecasting Endpoints
@router.post("/forecasts")
async def forecast_costs(tenant_id: str = "global", mgr: FinOpsManager = Depends(get_finops)):
    fc = mgr.forecasting_engine.forecast_spend(tenant_id=tenant_id)
    return {"forecast": fc.model_dump()}


# 4. Optimization Endpoints
@router.get("/optimizations")
async def list_optimizations(tenant_id: str = "global", mgr: FinOpsManager = Depends(get_finops)):
    recs = mgr.optimization_engine.generate_recommendations(tenant_id=tenant_id)
    return {"recommendations": [r.model_dump() for r in recs]}


@router.post("/optimizations/{id}/approve")
async def approve_optimization(id: str, mgr: FinOpsManager = Depends(get_finops)):
    try:
        rec = mgr.optimization_engine.get_recommendation(id)
        decision = mgr.governance_engine.evaluate_optimization(rec)
        return {"decision": decision.model_dump()}
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Recommendation '{id}' not found")


# 5. Capacity & Showback Endpoints
@router.get("/capacity")
async def get_capacity_plan(tenant_id: str = "global", mgr: FinOpsManager = Depends(get_finops)):
    recs = mgr.capacity_planner.analyze_capacity(tenant_id=tenant_id)
    return {"capacity_recommendations": [r.model_dump() for r in recs]}


@router.get("/showback")
async def get_showback_report(tenant_id: str = "global", mgr: FinOpsManager = Depends(get_finops)):
    rep = mgr.chargeback_manager.generate_showback_report(tenant_id=tenant_id)
    return {"showback_report": rep.model_dump()}
