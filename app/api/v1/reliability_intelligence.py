"""FastAPI REST API Router for Reliability Intelligence (Phase 5.55)."""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, Header, status

from app.reliability_intelligence.manager import ReliabilityIntelligenceManager
from app.reliability_intelligence.schemas import (
    ChaosProposalRequest,
    ChaosProposalResponse,
    DegradationPlanRequest,
    DegradationPlanResponse,
    ErrorBudgetResponse,
    GovernanceRequest,
    GovernanceResponse,
    PredictionRequest,
    PredictionResponse,
    PropagationRequest,
    PropagationResponse,
    RecoveryPlanRequest,
    RecoveryPlanResponse,
    ReliabilityAssessmentRequest,
    ReliabilityAssessmentResponse,
    ServiceHealthRequest,
    ServiceHealthResponse,
    SLORequest,
    SLOResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/reliability", tags=["Reliability Intelligence"])

_manager_instance: Optional[ReliabilityIntelligenceManager] = None


def get_reliability_manager() -> ReliabilityIntelligenceManager:
    global _manager_instance
    if _manager_instance is None:
        _manager_instance = ReliabilityIntelligenceManager()
    return _manager_instance


@router.get("/metrics")
def get_metrics(mgr: ReliabilityIntelligenceManager = Depends(get_reliability_manager)):
    return mgr.observability.get_metrics()


# Service Health
@router.post("/health", response_model=ServiceHealthResponse, status_code=status.HTTP_201_CREATED)
def evaluate_service_health(
    req: ServiceHealthRequest,
    x_tenant_id: str = Header("default_tenant", alias="X-Tenant-ID"),
    mgr: ReliabilityIntelligenceManager = Depends(get_reliability_manager),
):
    sh = mgr.evaluate_service_health(tenant_id=x_tenant_id, service_id=req.service_id, raw_metrics=req.metrics)
    return ServiceHealthResponse(
        assessment_id=sh.assessment_id,
        tenant_id=sh.tenant_id,
        service_id=sh.service_id,
        status=sh.status.value,
        overall_score=sh.overall_score,
        evaluated_at=sh.evaluated_at,
    )


# Reliability Assessments
@router.post("/assessments", response_model=ReliabilityAssessmentResponse)
def evaluate_reliability(
    req: ReliabilityAssessmentRequest,
    x_tenant_id: str = Header("default_tenant", alias="X-Tenant-ID"),
    mgr: ReliabilityIntelligenceManager = Depends(get_reliability_manager),
):
    ass = mgr.evaluate_reliability(tenant_id=x_tenant_id, scope=req.scope)
    return ReliabilityAssessmentResponse(
        assessment_id=ass.assessment_id,
        tenant_id=ass.tenant_id,
        overall_score=ass.score.overall_score,
        state=ass.state.value,
        findings_count=len(ass.findings),
        created_at=ass.created_at,
    )


# SLO & Error Budgets
@router.post("/slo", response_model=SLOResponse)
def create_slo(
    req: SLORequest,
    x_tenant_id: str = Header("default_tenant", alias="X-Tenant-ID"),
    mgr: ReliabilityIntelligenceManager = Depends(get_reliability_manager),
):
    slo = mgr.create_slo(
        tenant_id=x_tenant_id,
        service_id=req.service_id,
        indicator_type=req.indicator_type,
        target_percentage=req.target_percentage,
    )
    return SLOResponse(
        slo_id=slo.slo_id,
        tenant_id=slo.tenant_id,
        service_id=slo.service_id,
        indicator_type=slo.indicator_type,
        target_percentage=slo.target_percentage,
        current_percentage=slo.current_percentage,
        is_breached=slo.is_breached,
    )


@router.post("/error-budgets", response_model=ErrorBudgetResponse)
def evaluate_error_budget(
    slo_id: str,
    x_tenant_id: str = Header("default_tenant", alias="X-Tenant-ID"),
    mgr: ReliabilityIntelligenceManager = Depends(get_reliability_manager),
):
    eb = mgr.evaluate_error_budget(tenant_id=x_tenant_id, slo_id=slo_id)
    return ErrorBudgetResponse(
        slo_id=eb.slo_id,
        tenant_id=eb.tenant_id,
        total_budget_minutes=eb.total_budget_minutes,
        remaining_budget_minutes=eb.remaining_budget_minutes,
        status=eb.status.value,
        burn_rate=eb.burn_rate,
    )


# Failure Predictions
@router.post("/predictions", response_model=PredictionResponse)
def predict_failure(
    req: PredictionRequest,
    x_tenant_id: str = Header("default_tenant", alias="X-Tenant-ID"),
    mgr: ReliabilityIntelligenceManager = Depends(get_reliability_manager),
):
    pred = mgr.predict_failure(tenant_id=x_tenant_id, service_id=req.service_id, horizon_minutes=req.horizon_minutes)
    return PredictionResponse(
        prediction_id=pred.prediction_id,
        tenant_id=pred.tenant_id,
        service_id=pred.service_id,
        predicted_failure_type=pred.predicted_failure_type.value,
        probability=pred.probability,
        confidence=pred.confidence,
        explanation=pred.explanation,
        created_at=pred.created_at,
    )


# Propagation Analysis
@router.post("/propagation/analyze", response_model=PropagationResponse)
def analyze_propagation(
    req: PropagationRequest,
    x_tenant_id: str = Header("default_tenant", alias="X-Tenant-ID"),
    mgr: ReliabilityIntelligenceManager = Depends(get_reliability_manager),
):
    path = mgr.analyze_propagation(
        tenant_id=x_tenant_id, origin_service=req.origin_service, downstream_services=["svc_db", "svc_auth"]
    )
    return PropagationResponse(
        path_id=path.path_id,
        tenant_id=path.tenant_id,
        origin_service=path.origin_service,
        affected_nodes=path.affected_nodes,
        propagation_probability=path.propagation_probability,
        blast_radius_score=path.blast_radius_score,
    )


# Degradation & Recovery
@router.post("/degradation/plan", response_model=DegradationPlanResponse)
def plan_degradation(
    req: DegradationPlanRequest,
    x_tenant_id: str = Header("default_tenant", alias="X-Tenant-ID"),
    mgr: ReliabilityIntelligenceManager = Depends(get_reliability_manager),
):
    plan = mgr.plan_degradation(tenant_id=x_tenant_id, service_id=req.service_id, strategy=req.strategy)
    return DegradationPlanResponse(
        plan_id=plan.plan_id,
        tenant_id=plan.tenant_id,
        service_id=plan.service_id,
        strategy=plan.strategy.value,
        requires_approval=plan.requires_approval,
    )


@router.post("/recovery/plan", response_model=RecoveryPlanResponse)
def plan_recovery(
    req: RecoveryPlanRequest,
    x_tenant_id: str = Header("default_tenant", alias="X-Tenant-ID"),
    mgr: ReliabilityIntelligenceManager = Depends(get_reliability_manager),
):
    plan = mgr.plan_recovery(tenant_id=x_tenant_id, service_id=req.service_id, strategy=req.strategy)
    return RecoveryPlanResponse(
        plan_id=plan.plan_id,
        tenant_id=plan.tenant_id,
        service_id=plan.service_id,
        strategy=plan.strategy.value,
        estimated_rto_minutes=plan.estimated_rto_minutes,
    )


# Chaos Governance
@router.post("/chaos/propose", response_model=ChaosProposalResponse)
def propose_chaos(
    req: ChaosProposalRequest,
    x_tenant_id: str = Header("default_tenant", alias="X-Tenant-ID"),
    mgr: ReliabilityIntelligenceManager = Depends(get_reliability_manager),
):
    prop = mgr.propose_chaos_experiment(
        tenant_id=x_tenant_id,
        experiment_name=req.experiment_name,
        target_service=req.target_service,
        hypothesis=req.hypothesis,
    )
    return ChaosProposalResponse(
        proposal_id=prop.proposal_id,
        tenant_id=prop.tenant_id,
        experiment_name=prop.experiment_name,
        target_service=prop.target_service,
        risk_level=prop.risk_level,
        requires_approval=prop.requires_approval,
        auto_execute=prop.auto_execute,
    )


# Governance
@router.post("/governance/evaluate", response_model=GovernanceResponse)
def evaluate_governance(
    req: GovernanceRequest,
    x_tenant_id: str = Header("default_tenant", alias="X-Tenant-ID"),
    mgr: ReliabilityIntelligenceManager = Depends(get_reliability_manager),
):
    res = mgr.evaluate_governance(tenant_id=x_tenant_id, action_type=req.action_type, risk_level=req.risk_level)
    return GovernanceResponse(**res)


# Analytics
@router.get("/analytics")
def get_analytics(
    x_tenant_id: str = Header("default_tenant", alias="X-Tenant-ID"),
    mgr: ReliabilityIntelligenceManager = Depends(get_reliability_manager),
):
    return mgr.analytics.generate_report(tenant_id=x_tenant_id)
