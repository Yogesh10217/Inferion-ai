"""FastAPI REST API Router for Capacity Intelligence (Phase 5.56)."""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException, status

from app.capacity_intelligence.manager import CapacityIntelligenceManager
from app.capacity_intelligence.schemas import (
    BottleneckDetectionRequest,
    BottleneckDetectionResponse,
    CapacityAssessmentRequest,
    CapacityAssessmentResponse,
    CapacityForecastRequest,
    CapacityForecastResponse,
    CostPerformanceRequest,
    CostPerformanceResponse,
    DelegationRequestSchema,
    DelegationResponseSchema,
    DemandPredictionRequest,
    DemandPredictionResponse,
    EvidenceBundleResponse,
    GovernanceRequest,
    GovernanceResponse,
    OptimizationRequest,
    OptimizationResponse,
    ResourceRegistrationRequest,
    ResourceRegistrationResponse,
    SaturationAnalysisRequest,
    SaturationAnalysisResponse,
    SnapshotResponse,
    TelemetryIngestionRequest,
    TelemetryIngestionResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1/capacity", tags=["Capacity Intelligence"])

_manager_instance: Optional[CapacityIntelligenceManager] = None


def get_capacity_manager() -> CapacityIntelligenceManager:
    global _manager_instance
    if _manager_instance is None:
        _manager_instance = CapacityIntelligenceManager()
    return _manager_instance


@router.get("/metrics")
def get_metrics(mgr: CapacityIntelligenceManager = Depends(get_capacity_manager)):
    return mgr.observability.get_metrics()


# Resource & Telemetry
@router.post("/resources", response_model=ResourceRegistrationResponse, status_code=status.HTTP_201_CREATED)
def register_resource(
    req: ResourceRegistrationRequest,
    x_tenant_id: str = Header("default_tenant", alias="X-Tenant-ID"),
    mgr: CapacityIntelligenceManager = Depends(get_capacity_manager),
):
    res = mgr.register_resource(
        tenant_id=x_tenant_id,
        resource_id=req.resource_id,
        name=req.name,
        resource_type=req.resource_type,
        total_capacity=req.total_capacity,
        capacity_unit=req.capacity_unit,
    )
    return ResourceRegistrationResponse(
        resource_id=res.resource_id,
        tenant_id=res.tenant_id,
        name=res.name,
        resource_type=res.resource_type,
        total_capacity=res.total_capacity,
        capacity_unit=res.capacity_unit,
        registered_at=res.registered_at,
    )


@router.post("/telemetry", response_model=TelemetryIngestionResponse, status_code=status.HTTP_201_CREATED)
def ingest_telemetry(
    req: TelemetryIngestionRequest,
    x_tenant_id: str = Header("default_tenant", alias="X-Tenant-ID"),
    mgr: CapacityIntelligenceManager = Depends(get_capacity_manager),
):
    tel = mgr.ingest_telemetry(
        tenant_id=x_tenant_id,
        resource_id=req.resource_id,
        metric_name=req.metric_name,
        value=req.value,
        timestamp=req.timestamp,
    )
    return TelemetryIngestionResponse(
        telemetry_id=tel.telemetry_id,
        tenant_id=tel.tenant_id,
        resource_id=tel.resource_id,
        metric_name=tel.metric_name,
        value=tel.value,
        timestamp=tel.timestamp,
    )


# Assessment & Forecasting
@router.post("/assessments", response_model=CapacityAssessmentResponse)
def assess_capacity(
    req: CapacityAssessmentRequest,
    x_tenant_id: str = Header("default_tenant", alias="X-Tenant-ID"),
    mgr: CapacityIntelligenceManager = Depends(get_capacity_manager),
):
    ass = mgr.assess_capacity(
        tenant_id=x_tenant_id,
        resource_id=req.resource_id,
        scope=req.scope,
    )
    return CapacityAssessmentResponse(
        assessment_id=ass.assessment_id,
        tenant_id=ass.tenant_id,
        resource_id=ass.resource_id,
        utilization_rate=ass.utilization_rate,
        health_status=ass.health_status,
        assessed_at=ass.assessed_at,
    )


@router.post("/forecasts", response_model=CapacityForecastResponse)
def forecast_capacity(
    req: CapacityForecastRequest,
    x_tenant_id: str = Header("default_tenant", alias="X-Tenant-ID"),
    mgr: CapacityIntelligenceManager = Depends(get_capacity_manager),
):
    fc = mgr.forecast_capacity(
        tenant_id=x_tenant_id,
        resource_id=req.resource_id,
        horizon_days=req.horizon_days,
    )
    return CapacityForecastResponse(
        forecast_id=fc.forecast_id,
        tenant_id=fc.tenant_id,
        resource_id=fc.resource_id,
        horizon_days=fc.horizon_days,
        predicted_utilization=fc.predicted_utilization,
        exhaustion_predicted=fc.exhaustion_predicted,
        forecasted_at=fc.created_at,
    )


# Demand & Saturation
@router.post("/demand", response_model=DemandPredictionResponse)
def predict_demand(
    req: DemandPredictionRequest,
    x_tenant_id: str = Header("default_tenant", alias="X-Tenant-ID"),
    mgr: CapacityIntelligenceManager = Depends(get_capacity_manager),
):
    dp = mgr.predict_demand(
        tenant_id=x_tenant_id,
        workload_type=req.workload_type,
        time_horizon_hours=req.time_horizon_hours,
    )
    return DemandPredictionResponse(
        prediction_id=dp.prediction_id,
        tenant_id=dp.tenant_id,
        workload_type=dp.workload_type,
        predicted_growth_rate=dp.predicted_growth_rate,
        confidence_score=dp.confidence_score,
        predicted_at=dp.predicted_at,
    )


@router.post("/saturation", response_model=SaturationAnalysisResponse)
def analyze_saturation(
    req: SaturationAnalysisRequest,
    x_tenant_id: str = Header("default_tenant", alias="X-Tenant-ID"),
    mgr: CapacityIntelligenceManager = Depends(get_capacity_manager),
):
    sa = mgr.analyze_saturation(
        tenant_id=x_tenant_id,
        resource_id=req.resource_id,
    )
    return SaturationAnalysisResponse(
        analysis_id=sa.analysis_id,
        tenant_id=sa.tenant_id,
        resource_id=sa.resource_id,
        saturation_level=sa.saturation_level,
        headroom_percent=sa.headroom_percent,
        analyzed_at=sa.analyzed_at,
    )


# Bottlenecks & Optimization
@router.post("/bottlenecks", response_model=BottleneckDetectionResponse)
def detect_bottlenecks(
    req: BottleneckDetectionRequest,
    x_tenant_id: str = Header("default_tenant", alias="X-Tenant-ID"),
    mgr: CapacityIntelligenceManager = Depends(get_capacity_manager),
):
    bn = mgr.detect_bottlenecks(
        tenant_id=x_tenant_id,
        system_scope=req.system_scope,
    )
    return BottleneckDetectionResponse(
        detection_id=bn.detection_id,
        tenant_id=bn.tenant_id,
        bottlenecks_found=len(bn.bottlenecks),
        critical_count=bn.critical_count,
        detected_at=bn.detected_at,
    )


@router.post("/optimizations", response_model=OptimizationResponse)
def optimize_capacity(
    req: OptimizationRequest,
    x_tenant_id: str = Header("default_tenant", alias="X-Tenant-ID"),
    mgr: CapacityIntelligenceManager = Depends(get_capacity_manager),
):
    opt = mgr.optimize_capacity(
        tenant_id=x_tenant_id,
        resource_id=req.resource_id,
        objective=req.objective,
    )
    return OptimizationResponse(
        plan_id=opt.plan_id,
        tenant_id=opt.tenant_id,
        resource_id=opt.resource_id,
        objective=opt.objective,
        auto_execute=opt.auto_execute,
        recommendations_count=len(opt.recommendations),
        created_at=opt.created_at,
    )


# Cost Performance & Governance
@router.post("/cost-performance", response_model=CostPerformanceResponse)
def evaluate_cost_performance(
    req: CostPerformanceRequest,
    x_tenant_id: str = Header("default_tenant", alias="X-Tenant-ID"),
    mgr: CapacityIntelligenceManager = Depends(get_capacity_manager),
):
    cp = mgr.evaluate_cost_performance(
        tenant_id=x_tenant_id,
        resource_id=req.resource_id,
    )
    return CostPerformanceResponse(
        assessment_id=cp.assessment_id,
        tenant_id=cp.tenant_id,
        resource_id=cp.resource_id,
        efficiency_score=cp.efficiency_score,
        cost_per_unit=cp.cost_per_unit,
        evaluated_at=cp.evaluated_at,
    )


@router.post("/governance/evaluate", response_model=GovernanceResponse)
def evaluate_governance(
    req: GovernanceRequest,
    x_tenant_id: str = Header("default_tenant", alias="X-Tenant-ID"),
    mgr: CapacityIntelligenceManager = Depends(get_capacity_manager),
):
    gov = mgr.evaluate_governance(
        tenant_id=x_tenant_id,
        action=req.action,
        risk_level=req.risk_level,
    )
    return GovernanceResponse(
        evaluation_id=gov["evaluation_id"],
        tenant_id=x_tenant_id,
        decision=gov["decision"],
        requires_human_approval=gov["requires_human_approval"],
        reasoning=gov["reasoning"],
    )


# Delegation
@router.post("/delegation", response_model=DelegationResponseSchema)
def request_delegation(
    req: DelegationRequestSchema,
    x_tenant_id: str = Header("default_tenant", alias="X-Tenant-ID"),
    mgr: CapacityIntelligenceManager = Depends(get_capacity_manager),
):
    del_req = mgr.request_delegation(
        tenant_id=x_tenant_id,
        target_domain=req.target_domain,
        action_type=req.action_type,
        payload=req.payload,
        risk_level=req.risk_level,
        is_approved=req.is_approved,
    )
    return DelegationResponseSchema(
        delegation_id=del_req.delegation_id,
        tenant_id=del_req.tenant_id,
        target_domain=del_req.target_domain,
        action_type=del_req.action_type,
        status=del_req.status.value,
        requires_approval=del_req.requires_approval,
        created_at=del_req.created_at,
    )


# Evidence & Snapshots
@router.get("/evidence/{evidence_id}", response_model=EvidenceBundleResponse)
def get_evidence(
    evidence_id: str,
    x_tenant_id: str = Header("default_tenant", alias="X-Tenant-ID"),
    mgr: CapacityIntelligenceManager = Depends(get_capacity_manager),
):
    eb = mgr.get_evidence(tenant_id=x_tenant_id, evidence_id=evidence_id)
    if not eb:
        raise HTTPException(status_code=404, detail="Evidence bundle not found")
    return EvidenceBundleResponse(
        bundle_id=eb.bundle_id,
        tenant_id=eb.tenant_id,
        evidence_count=len(eb.records),
        sealed=eb.sealed,
        integrity_hash=eb.integrity_hash,
        created_at=eb.created_at,
    )


@router.post("/snapshots", response_model=SnapshotResponse)
def capture_snapshot(
    x_tenant_id: str = Header("default_tenant", alias="X-Tenant-ID"),
    mgr: CapacityIntelligenceManager = Depends(get_capacity_manager),
):
    snap = mgr.capture_snapshot(tenant_id=x_tenant_id)
    return SnapshotResponse(
        snapshot_id=snap.snapshot_id,
        tenant_id=snap.tenant_id,
        captured_at=snap.captured_at,
        records_count=snap.records_count,
        integrity_hash=snap.integrity_hash,
    )
