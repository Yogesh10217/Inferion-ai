"""REST API Endpoints for Enterprise AI Decision Intelligence Platform (Phase 5.29)."""

from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, Header, HTTPException, status

from app.decision_intelligence.exceptions import (
    CrossTenantDecisionAccessException,
    DecisionNotFoundException,
    ImmutableDecisionException,
)
from app.decision_intelligence.manager import DecisionIntelligenceManager
from app.decision_intelligence.scenarios import ScenarioType

router = APIRouter(prefix="/decisions", tags=["decision-intelligence"])
mgr = DecisionIntelligenceManager()


def _get_tenant_id(x_tenant_id: Optional[str] = Header(None, alias="X-Tenant-ID")) -> str:
    return x_tenant_id or "global"


@router.post("/context")
async def create_decision_context(
    payload: Dict[str, Any],
    tenant_id: str = Depends(_get_tenant_id),
):
    """Create enterprise decision context."""
    title = payload.get("title", "Decision Context")
    desc = payload.get("description", "Description")

    ctx = mgr.context_builder.assemble_context(
        tenant_id=tenant_id,
        title=title,
        description=desc,
    )
    res = mgr.context_manager.create_context(ctx)
    return res.model_dump()


@router.post("/scenarios")
async def create_scenario(
    payload: Dict[str, Any],
    tenant_id: str = Depends(_get_tenant_id),
):
    """Create decision scenario."""
    ctx_id = payload.get("context_id")
    title = payload.get("title", "Scenario")
    scen_type = ScenarioType(payload.get("scenario_type", "BASELINE"))

    if not ctx_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="context_id is required.")

    scen = mgr.scenario_manager.create_scenario(tenant_id, ctx_id, title, scen_type)
    sim = mgr.scenario_manager.simulate_scenario(scen.scenario_id, tenant_id)
    return sim.model_dump()


@router.post("/analyze")
async def analyze_decision(
    payload: Dict[str, Any],
    tenant_id: str = Depends(_get_tenant_id),
):
    """Analyze decision risk, trust, and trade-offs."""
    title = payload.get("title", "Enterprise Decision Analysis")
    flow_res = mgr.run_full_decision_flow(tenant_id=tenant_id, title=title)
    return flow_res


@router.get("/{decision_id}")
async def get_decision(
    decision_id: str,
    tenant_id: str = Depends(_get_tenant_id),
):
    """Get decision by ID."""
    try:
        dec = mgr.decision_manager.get_decision(decision_id, tenant_id)
        return dec.model_dump()
    except CrossTenantDecisionAccessException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Decision not found.")
    except DecisionNotFoundException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Decision not found.")


@router.post("/{decision_id}/finalize")
async def finalize_decision(
    decision_id: str,
    tenant_id: str = Depends(_get_tenant_id),
):
    """Finalize decision and create immutable snapshot."""
    try:
        dec = mgr.decision_manager.finalize_decision(decision_id, tenant_id)
        return dec.model_dump()
    except ImmutableDecisionException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)


@router.get("/analytics")
async def get_analytics(
    tenant_id: str = Depends(_get_tenant_id),
):
    """Get decision analytics report."""
    report = mgr.analytics_engine.generate_report(tenant_id)
    return report.model_dump()
