"""FastAPI REST API Router for Runtime Intelligence (Phase 5.54)."""

import logging
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Header, status

from app.runtime_intelligence.manager import RuntimeIntelligenceManager
from app.runtime_intelligence.schemas import (
    RuntimeObservationRequest,
    RuntimeObservationResponse,
    HealthAssessmentRequest,
    HealthAssessmentResponse,
    AnomalyDetectionRequest,
    AnomalyDetectionResponse,
    DriftAnalysisRequest,
    DriftAnalysisResponse,
    BaselineRequest,
    BaselineResponse,
    DegradationRequest,
    DegradationResponse,
    CausalAnalysisRequest,
    CausalAnalysisResponse,
    ResilienceAssessmentRequest,
    ResilienceAssessmentResponse,
    RecoveryPlanRequest,
    RecoveryPlanResponse,
    AdaptiveAssuranceRequest,
    AdaptiveAssuranceResponse,
    RecommendationRequest,
    RecommendationResponse,
    GovernanceEvaluationRequest,
    GovernanceEvaluationResponse,
    DelegationRequestSchema,
    DelegationResponseSchema,
    EvidenceBundleResponse,
    SnapshotResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1/runtime", tags=["Runtime Intelligence"])

_manager_instance: Optional[RuntimeIntelligenceManager] = None

def get_runtime_manager() -> RuntimeIntelligenceManager:
    global _manager_instance
    if _manager_instance is None:
        _manager_instance = RuntimeIntelligenceManager()
    return _manager_instance


@router.get("/metrics")
def get_metrics(mgr: RuntimeIntelligenceManager = Depends(get_runtime_manager)):
    return mgr.observability.get_metrics()


# Signal Ingestion
@router.post("/observations", response_model=RuntimeObservationResponse, status_code=status.HTTP_201_CREATED)
def ingest_observation(
    req: RuntimeObservationRequest,
    x_tenant_id: str = Header("default_tenant", alias="X-Tenant-ID"),
    mgr: RuntimeIntelligenceManager = Depends(get_runtime_manager),
):
    obs = mgr.ingest_observation(
        tenant_id=x_tenant_id,
        subsystem=req.subsystem,
        metric_name=req.metric_name,
        value=req.value,
        dimensions=req.dimensions,
    )
    return RuntimeObservationResponse(
        observation_id=obs.observation_id,
        tenant_id=obs.tenant_id,
        subsystem=obs.subsystem,
        metric_name=obs.metric_name,
        value=obs.value,
        observed_at=obs.observed_at,
    )


# Health Assessment
@router.post("/health", response_model=HealthAssessmentResponse)
def evaluate_health(
    req: HealthAssessmentRequest,
    x_tenant_id: str = Header("default_tenant", alias="X-Tenant-ID"),
    mgr: RuntimeIntelligenceManager = Depends(get_runtime_manager),
):
    ha = mgr.evaluate_health(
        tenant_id=x_tenant_id,
        subsystem=req.subsystem,
        telemetry=req.raw_telemetry,
    )
    return HealthAssessmentResponse(
        health_id=ha.assessment_id,
        tenant_id=ha.tenant_id,
        subsystem=ha.subsystem,
        status=ha.overall_health.value,
        overall_score=ha.overall_score,
        evaluated_at=ha.evaluated_at,
    )


# Anomaly Detection
@router.post("/anomalies", response_model=AnomalyDetectionResponse)
def detect_anomalies(
    req: AnomalyDetectionRequest,
    x_tenant_id: str = Header("default_tenant", alias="X-Tenant-ID"),
    mgr: RuntimeIntelligenceManager = Depends(get_runtime_manager),
):
    res = mgr.detect_anomalies(
        tenant_id=x_tenant_id,
        subsystem=req.subsystem,
        time_series_data=req.time_series_data,
    )
    return AnomalyDetectionResponse(
        detection_id=res["detection_id"],
        tenant_id=x_tenant_id,
        subsystem=req.subsystem,
        anomalies_found=res["anomalies_count"],
        highest_severity=res["highest_severity"],
        detected_at=res["detected_at"],
    )


# Drift Analysis
@router.post("/drift", response_model=DriftAnalysisResponse)
def detect_drift(
    req: DriftAnalysisRequest,
    x_tenant_id: str = Header("default_tenant", alias="X-Tenant-ID"),
    mgr: RuntimeIntelligenceManager = Depends(get_runtime_manager),
):
    dr = mgr.detect_drift(
        tenant_id=x_tenant_id,
        subsystem=req.subsystem,
        current_data=req.current_data,
        baseline_data=req.baseline_data,
    )
    return DriftAnalysisResponse(
        drift_id=dr.drift_id,
        tenant_id=dr.tenant_id,
        subsystem=dr.subsystem,
        drift_detected=dr.drift_detected,
        drift_score=dr.drift_score,
        analyzed_at=dr.detected_at,
    )


# Baseline Management
@router.post("/baseline", response_model=BaselineResponse)
def establish_baseline(
    req: BaselineRequest,
    x_tenant_id: str = Header("default_tenant", alias="X-Tenant-ID"),
    mgr: RuntimeIntelligenceManager = Depends(get_runtime_manager),
):
    bl = mgr.establish_baseline(
        tenant_id=x_tenant_id,
        subsystem=req.subsystem,
        metric_name=req.metric_name,
        sample_values=req.sample_values,
    )
    return BaselineResponse(
        baseline_id=bl.baseline_id,
        tenant_id=bl.tenant_id,
        subsystem=bl.subsystem,
        metric_name=bl.metric_name,
        mean=bl.mean,
        std_dev=bl.std_dev,
        sample_count=bl.sample_count,
        established_at=bl.established_at,
    )


# Causal & Risk Analysis
@router.post("/causal-analysis", response_model=CausalAnalysisResponse)
def analyze_causality(
    req: CausalAnalysisRequest,
    x_tenant_id: str = Header("default_tenant", alias="X-Tenant-ID"),
    mgr: RuntimeIntelligenceManager = Depends(get_runtime_manager),
):
    ca = mgr.analyze_causality(
        tenant_id=x_tenant_id,
        symptom_id=req.symptom_id,
        affected_subsystems=req.affected_subsystems,
    )
    return CausalAnalysisResponse(
        analysis_id=ca.analysis_id,
        tenant_id=ca.tenant_id,
        symptom_id=ca.symptom_id,
        root_cause=ca.root_cause_summary,
        confidence_score=ca.confidence_score,
        analyzed_at=ca.analyzed_at,
    )


# Resilience Assessment
@router.post("/resilience", response_model=ResilienceAssessmentResponse)
def evaluate_resilience(
    req: ResilienceAssessmentRequest,
    x_tenant_id: str = Header("default_tenant", alias="X-Tenant-ID"),
    mgr: RuntimeIntelligenceManager = Depends(get_runtime_manager),
):
    ra = mgr.evaluate_resilience(
        tenant_id=x_tenant_id,
        subsystem=req.subsystem,
    )
    return ResilienceAssessmentResponse(
        assessment_id=ra.assessment_id,
        tenant_id=ra.tenant_id,
        subsystem=ra.subsystem,
        resilience_score=ra.resilience_score,
        overall_status=ra.status.value,
        evaluated_at=ra.evaluated_at,
    )


# Adaptive Assurance & Governance
@router.post("/adaptive-assurance", response_model=AdaptiveAssuranceResponse)
def adapt_assurance(
    req: AdaptiveAssuranceRequest,
    x_tenant_id: str = Header("default_tenant", alias="X-Tenant-ID"),
    mgr: RuntimeIntelligenceManager = Depends(get_runtime_manager),
):
    aa = mgr.evaluate_adaptive_assurance(
        tenant_id=x_tenant_id,
        target_subsystem=req.target_subsystem,
    )
    return AdaptiveAssuranceResponse(
        posture_id=aa.posture_id,
        tenant_id=aa.tenant_id,
        target_subsystem=aa.target_subsystem,
        current_level=aa.current_level.value,
        recommended_level=aa.recommended_level.value,
        evaluated_at=aa.evaluated_at,
    )


@router.post("/governance/evaluate", response_model=GovernanceEvaluationResponse)
def evaluate_governance(
    req: GovernanceEvaluationRequest,
    x_tenant_id: str = Header("default_tenant", alias="X-Tenant-ID"),
    mgr: RuntimeIntelligenceManager = Depends(get_runtime_manager),
):
    gr = mgr.evaluate_governance(
        tenant_id=x_tenant_id,
        action=req.action,
        risk_level=req.risk_level,
    )
    return GovernanceEvaluationResponse(
        evaluation_id=gr["evaluation_id"],
        tenant_id=x_tenant_id,
        decision=gr["decision"],
        requires_human_approval=gr["requires_human_approval"],
        reasoning=gr["reasoning"],
    )


# Delegation
@router.post("/delegation", response_model=DelegationResponseSchema)
def request_delegation(
    req: DelegationRequestSchema,
    x_tenant_id: str = Header("default_tenant", alias="X-Tenant-ID"),
    mgr: RuntimeIntelligenceManager = Depends(get_runtime_manager),
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
    mgr: RuntimeIntelligenceManager = Depends(get_runtime_manager),
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
    mgr: RuntimeIntelligenceManager = Depends(get_runtime_manager),
):
    snap = mgr.capture_snapshot(tenant_id=x_tenant_id)
    return SnapshotResponse(
        snapshot_id=snap.snapshot_id,
        tenant_id=snap.tenant_id,
        captured_at=snap.captured_at,
        records_count=snap.records_count,
        integrity_hash=snap.integrity_hash,
    )
