"""REST API Endpoints for Enterprise AI Intelligence & Decision Platform."""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, status
from pydantic import BaseModel

from app.intelligence_platform.execution import ExecutionTarget
from app.intelligence_platform.forecasting import ForecastHorizon, ForecastType
from app.intelligence_platform.manager import EnterpriseIntelligenceManager
from app.intelligence_platform.optimization import OptimizationCandidate, OptimizationObjective
from app.intelligence_platform.recommendations import RecommendationType
from app.intelligence_platform.signals import SignalClassification, SignalSource, SignalType
from app.intelligence_platform.simulation import SimulationInput, SimulationScenario

router = APIRouter(prefix="/v1/intelligence", tags=["intelligence-platform"])

mgr = EnterpriseIntelligenceManager()


class SignalIngestRequest(BaseModel):
    source: SignalSource
    signal_type: SignalType
    message: str
    tenant_id: str = "global"
    classification: SignalClassification = SignalClassification.OBSERVATION
    metrics: Dict[str, float] = {}
    payload: Dict[str, Any] = {}
    resource_id: Optional[str] = None


class ForecastRequest(BaseModel):
    target_resource_id: str
    forecast_type: ForecastType = ForecastType.INCIDENT_RISK_FORECAST
    horizon: ForecastHorizon = ForecastHorizon.NEAR_TERM
    tenant_id: str = "global"


class SimulationRequest(BaseModel):
    scenario: SimulationScenario = SimulationScenario.WHAT_IF
    target_resource_id: str
    action_type: str = "ROLLBACK"
    tenant_id: str = "global"


class OptimizationRequest(BaseModel):
    objective: OptimizationObjective = OptimizationObjective.MINIMIZE_RISK
    candidates: List[Dict[str, Any]]
    tenant_id: str = "global"


class RecommendRequest(BaseModel):
    recommendation_type: RecommendationType
    title: str
    action_description: str
    target_resource_id: str
    expected_impact: str = "Risk reduction"
    tenant_id: str = "global"
    risk_level: str = "LOW"


class DecisionApproveRequest(BaseModel):
    reviewer_user_id: str = "admin"
    tenant_id: str = "global"


class DecisionExecuteRequest(BaseModel):
    target: ExecutionTarget = ExecutionTarget.PLATFORM_OPERATIONS
    tenant_id: str = "global"


@router.post("/signals", status_code=status.HTTP_202_ACCEPTED)
def ingest_signal(req: SignalIngestRequest):
    sig = mgr.signal_manager.ingest_signal(
        tenant_id=req.tenant_id,
        source=req.source,
        signal_type=req.signal_type,
        message=req.message,
        classification=req.classification,
        metrics=req.metrics,
        payload=req.payload,
        resource_id=req.resource_id,
    )
    return sig.model_dump(mode="json")


@router.post("/analyze")
def run_analysis(tenant_id: str = "global", resource_id: str = "res_1"):
    signals = mgr.signal_manager.list_signals(tenant_id, resource_id=resource_id)
    ctx = mgr.context_builder.assemble_context(tenant_id, primary_resource_id=resource_id, signals=signals)
    insight = mgr.insight_manager.generate_insight_from_context(
        tenant_id=tenant_id,
        insight_type="OPERATIONAL",
        observation=f"Resource '{resource_id}' evaluated.",
        recommended_next_step="Maintain operational parameters",
        context=ctx,
    )
    return {"context": ctx.model_dump(mode="json"), "insight": insight.model_dump(mode="json")}


@router.post("/forecast")
def generate_forecast(req: ForecastRequest):
    signals = mgr.signal_manager.list_signals(req.tenant_id, resource_id=req.target_resource_id)
    ctx = mgr.context_builder.assemble_context(req.tenant_id, primary_resource_id=req.target_resource_id, signals=signals)
    fc = mgr.forecast_engine.forecast(req.tenant_id, req.target_resource_id, req.forecast_type, ctx, horizon=req.horizon)
    return fc.model_dump(mode="json")


@router.post("/simulate")
def run_simulation(req: SimulationRequest):
    signals = mgr.signal_manager.list_signals(req.tenant_id, resource_id=req.target_resource_id)
    ctx = mgr.context_builder.assemble_context(req.tenant_id, primary_resource_id=req.target_resource_id, signals=signals)
    sim_in = SimulationInput(scenario_name=req.scenario.value, target_resource_id=req.target_resource_id, action_type=req.action_type)
    res = mgr.simulation_engine.simulate(req.tenant_id, req.scenario, sim_in, ctx)
    return res.model_dump(mode="json")


@router.post("/optimize")
def run_optimization(req: OptimizationRequest):
    cand_objs = [OptimizationCandidate(**c) for c in req.candidates]
    res = mgr.optimization_engine.optimize(req.tenant_id, req.objective, cand_objs)
    return res.model_dump(mode="json")


@router.post("/recommend")
def create_recommendation(req: RecommendRequest):
    rec = mgr.recommendation_manager.create_recommendation(
        tenant_id=req.tenant_id,
        recommendation_type=req.recommendation_type,
        title=req.title,
        action_description=req.action_description,
        target_resource_id=req.target_resource_id,
        expected_impact=req.expected_impact,
        risk_level=req.risk_level,
    )
    return rec.model_dump(mode="json")


@router.post("/decisions")
def create_decision(tenant_id: str = "global", title: str = "Sample Decision"):
    dec = mgr.decision_manager.create_decision(tenant_id=tenant_id, title=title)
    return dec.model_dump(mode="json")


@router.post("/decisions/{decision_id}/approve")
def approve_decision(decision_id: str, req: DecisionApproveRequest):
    dec = mgr.decision_manager.get_decision(decision_id, req.tenant_id)
    updated = mgr.decision_manager.update_status(decision_id, req.tenant_id, "APPROVED")
    return updated.model_dump(mode="json")


@router.post("/decisions/{decision_id}/execute")
def execute_decision(decision_id: str, req: DecisionExecuteRequest):
    dec = mgr.decision_manager.get_decision(decision_id, req.tenant_id)
    rec = mgr.recommendation_manager.create_recommendation(
        tenant_id=req.tenant_id,
        recommendation_type=RecommendationType.ROLLBACK_DEPLOYMENT,
        title=dec.title,
        action_description="Execution delegated from decision",
        target_resource_id="res_exec",
        expected_impact="Recovery",
    )
    exec_res = mgr.execution_manager.delegate_execution(req.tenant_id, rec, req.target)
    return exec_res.model_dump(mode="json")


@router.get("/insights")
def list_insights(tenant_id: str = "global"):
    insights = mgr.insight_manager.list_insights(tenant_id)
    return [i.model_dump(mode="json") for i in insights]


@router.get("/recommendations")
def list_recommendations(tenant_id: str = "global"):
    recs = mgr.recommendation_manager.list_recommendations(tenant_id)
    return [r.model_dump(mode="json") for r in recs]


@router.get("/analytics")
def get_analytics(tenant_id: str = "global"):
    rep = mgr.analytics_engine.generate_report(tenant_id)
    return rep.model_dump(mode="json")
