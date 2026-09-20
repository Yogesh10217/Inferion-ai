"""REST API Endpoints for FinOps Intelligence Platform (Phase 5.42)."""

from typing import Any, Dict, List

from fastapi import APIRouter, Query, status
from pydantic import BaseModel

from app.finops_intelligence.manager import FinOpsIntelligenceManager

router = APIRouter(prefix="/finops", tags=["FinOps Intelligence"])
_mgr = FinOpsIntelligenceManager()


class CostRecordRequest(BaseModel):
    tenant_id: str
    category: str = "MODEL_INFERENCE"
    amount_usd: float


class BudgetCreateRequest(BaseModel):
    tenant_id: str
    name: str
    amount_usd: float
    warning_threshold_pct: float = 75.0
    critical_threshold_pct: float = 90.0


class OptimizationCreateRequest(BaseModel):
    tenant_id: str
    target_resource_id: str
    optimization_type: str = "MODEL_RIGHTSIZING"
    estimated_monthly_savings_usd: float
    action_summary: str
    is_high_risk: bool = False


@router.post("/costs", status_code=status.HTTP_201_CREATED)
def record_cost(req: CostRecordRequest) -> Dict[str, Any]:
    rec = _mgr.cost_manager.record_cost(
        tenant_id=req.tenant_id,
        category=req.category,  # type: ignore
        amount_usd=req.amount_usd,
    )
    _mgr.cost_repo.save(rec)
    return rec.model_dump(mode="json")


@router.get("/costs")
def list_costs(tenant_id: str = Query(..., description="Tenant ID")) -> List[Dict[str, Any]]:
    return [r.model_dump(mode="json") for r in _mgr.cost_repo.list(tenant_id)]


@router.post("/budgets", status_code=status.HTTP_201_CREATED)
def create_budget(req: BudgetCreateRequest) -> Dict[str, Any]:
    bdg = _mgr.budget_manager.create_budget(
        tenant_id=req.tenant_id,
        name=req.name,
        amount_usd=req.amount_usd,
        warning_threshold_pct=req.warning_threshold_pct,
        critical_threshold_pct=req.critical_threshold_pct,
    )
    _mgr.budget_repo.save(bdg)
    return bdg.model_dump(mode="json")


@router.get("/budgets")
def list_budgets(tenant_id: str = Query(..., description="Tenant ID")) -> List[Dict[str, Any]]:
    return [b.model_dump(mode="json") for b in _mgr.budget_repo.list(tenant_id)]


@router.post("/optimization", status_code=status.HTTP_201_CREATED)
def create_optimization(req: OptimizationCreateRequest) -> Dict[str, Any]:
    rec = _mgr.optimization_manager.create_recommendation(
        tenant_id=req.tenant_id,
        target_resource_id=req.target_resource_id,
        optimization_type=req.optimization_type,  # type: ignore
        estimated_monthly_savings_usd=req.estimated_monthly_savings_usd,
        action_summary=req.action_summary,
        is_high_risk=req.is_high_risk,
    )
    _mgr.optimization_repo.save(rec)
    return rec.model_dump(mode="json")


@router.get("/optimization")
def list_optimizations(tenant_id: str = Query(..., description="Tenant ID")) -> List[Dict[str, Any]]:
    return [r.model_dump(mode="json") for r in _mgr.optimization_repo.list(tenant_id)]


@router.get("/analytics")
def get_analytics(tenant_id: str = Query(..., description="Tenant ID")) -> Dict[str, Any]:
    rpt = _mgr.analytics_engine.generate_report(tenant_id)
    return rpt.model_dump(mode="json")
