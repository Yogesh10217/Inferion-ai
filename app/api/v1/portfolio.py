"""REST API Endpoints for Enterprise AI Portfolio Platform (Phase 5.28)."""

from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, Header, HTTPException, status

from app.portfolio_platform.exceptions import (
    FundingDecisionException,
)
from app.portfolio_platform.investment import InvestmentRisk
from app.portfolio_platform.manager import PortfolioPlatformManager
from app.portfolio_platform.strategy import StrategyHorizon

router = APIRouter(prefix="/portfolio", tags=["portfolio-platform"])
mgr = PortfolioPlatformManager()


def _get_tenant_id(x_tenant_id: Optional[str] = Header(None, alias="X-Tenant-ID")) -> str:
    return x_tenant_id or "global"


@router.post("/strategies")
async def create_strategy(
    payload: Dict[str, Any],
    tenant_id: str = Depends(_get_tenant_id),
):
    """Create enterprise AI strategy."""
    name = payload.get("name", "Enterprise Strategy")
    desc = payload.get("description", "Strategy")
    horizon = StrategyHorizon(payload.get("horizon", "NEAR_TERM"))

    strat = mgr.strategy_manager.create_strategy(tenant_id, name, desc, horizon)
    return strat.model_dump()


@router.get("/strategies")
async def list_strategies(
    tenant_id: str = Depends(_get_tenant_id),
):
    """List enterprise strategies."""
    strats = mgr.strategy_manager.list_strategies(tenant_id)
    return [s.model_dump() for s in strats]


@router.post("/opportunities")
async def discover_opportunity(
    payload: Dict[str, Any],
    tenant_id: str = Depends(_get_tenant_id),
):
    """Discover AI opportunity."""
    title = payload.get("title", "AI Opportunity")
    desc = payload.get("description", "Description")

    opp = mgr.opportunity_manager.discover_opportunity(tenant_id, title, desc)
    return opp.model_dump()


@router.get("/opportunities")
async def list_opportunities(
    tenant_id: str = Depends(_get_tenant_id),
):
    """List AI opportunities."""
    opps = mgr.opportunity_manager.list_opportunities(tenant_id)
    return [o.model_dump() for o in opps]


@router.post("/initiatives")
async def create_initiative(
    payload: Dict[str, Any],
    tenant_id: str = Depends(_get_tenant_id),
):
    """Create AI initiative."""
    title = payload.get("title", "AI Initiative")
    desc = payload.get("description", "Initiative Description")

    init = mgr.initiative_manager.create_initiative(tenant_id, title, desc)
    return init.model_dump()


@router.get("/initiatives")
async def list_initiatives(
    tenant_id: str = Depends(_get_tenant_id),
):
    """List AI initiatives."""
    inits = mgr.initiative_manager.list_initiatives(tenant_id)
    return [i.model_dump() for i in inits]


@router.post("/business-cases")
async def create_business_case(
    payload: Dict[str, Any],
    tenant_id: str = Depends(_get_tenant_id),
):
    """Create structured business case."""
    init_id = payload.get("initiative_id")
    problem = payload.get("problem_statement", "Problem statement")

    if not init_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="initiative_id is required.")

    bc = mgr.business_case_manager.create_business_case(tenant_id, init_id, problem)
    return bc.model_dump()


@router.post("/prioritize")
async def prioritize_portfolio(
    tenant_id: str = Depends(_get_tenant_id),
):
    """Prioritize portfolio initiatives."""
    inits = mgr.initiative_manager.list_initiatives(tenant_id)
    bcs = [mgr.business_case_manager.get_by_initiative(i.initiative_id, tenant_id) for i in inits]
    valid_bcs = [b for b in bcs if b is not None]

    prio = mgr.prioritization_engine.score_initiatives(tenant_id, inits, valid_bcs)
    return prio.model_dump()


@router.post("/optimize")
async def optimize_portfolio(
    tenant_id: str = Depends(_get_tenant_id),
):
    """Multi-objective portfolio optimization."""
    inits = mgr.initiative_manager.list_initiatives(tenant_id)
    bcs = [mgr.business_case_manager.get_by_initiative(i.initiative_id, tenant_id) for i in inits]
    valid_bcs = [b for b in bcs if b is not None]

    prio = mgr.prioritization_engine.score_initiatives(tenant_id, inits, valid_bcs)
    opt = mgr.optimization_engine.optimize_portfolio(tenant_id, prio, valid_bcs)
    return opt.model_dump()


@router.post("/investments")
async def propose_investment(
    payload: Dict[str, Any],
    tenant_id: str = Depends(_get_tenant_id),
):
    """Propose investment for initiative."""
    init_id = payload.get("initiative_id")
    amount = float(payload.get("amount_usd", 50000.0))
    risk = InvestmentRisk(payload.get("risk_level", "HIGH"))

    if not init_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="initiative_id is required.")

    prop = mgr.investment_manager.propose_investment(tenant_id, init_id, amount, risk)
    return prop.model_dump()


@router.post("/funding/allocate")
async def allocate_funding(
    payload: Dict[str, Any],
    tenant_id: str = Depends(_get_tenant_id),
):
    """Allocate budget funding with idempotency."""
    init_id = payload.get("initiative_id")
    idemp_key = payload.get("idempotency_key")
    amount = float(payload.get("amount_usd", 50000.0))

    if not init_id or not idemp_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="initiative_id and idempotency_key are required."
        )

    try:
        alloc = mgr.funding_manager.allocate_funding(tenant_id, init_id, idemp_key, amount)
        return alloc.model_dump()
    except FundingDecisionException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)


@router.get("/funding/envelope")
async def get_budget_envelope(
    tenant_id: str = Depends(_get_tenant_id),
):
    """Get budget envelope."""
    env = mgr.funding_manager.get_budget_envelope(tenant_id)
    return env.model_dump()


@router.get("/analytics")
async def get_analytics(
    tenant_id: str = Depends(_get_tenant_id),
):
    """Get portfolio analytics report."""
    report = mgr.analytics_engine.generate_report(tenant_id)
    return report.model_dump()
