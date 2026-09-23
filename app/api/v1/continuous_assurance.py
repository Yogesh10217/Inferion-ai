"""FastAPI REST API Router for Continuous Assurance (Phase 5.54)."""

import logging
from datetime import datetime, timezone
from typing import Dict, Optional

from fastapi import APIRouter, Depends, Header, status

from app.continuous_assurance.manager import ContinuousAssuranceManager
from app.continuous_assurance.schemas import (
    AssessmentRequest,
    AssessmentResponse,
    ControlEvaluationRequest,
    ControlEvaluationResponse,
    CreateObservationRequest,
    DelegationRequestSchema,
    DelegationResponse,
    DriftAnalysisRequest,
    DriftResponse,
    GovernanceEvaluationRequest,
    GovernanceEvaluationResponse,
    ObservationResponse,
    RecommendationRequest,
    RecommendationResponse,
    VerificationRequestSchema,
    VerificationResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/continuous-assurance", tags=["Continuous Assurance"])

# Dependency container provider helper
_manager_instance: Optional[ContinuousAssuranceManager] = None


def get_assurance_manager() -> ContinuousAssuranceManager:
    global _manager_instance
    if _manager_instance is None:
        _manager_instance = ContinuousAssuranceManager()
    return _manager_instance


@router.get("/health")
def get_health() -> Dict[str, str]:
    return {"status": "HEALTHY", "subsystem": "continuous_assurance", "phase": "5.54"}


# Observations
@router.post("/observations", response_model=ObservationResponse, status_code=status.HTTP_201_CREATED)
def create_observation(
    req: CreateObservationRequest,
    x_tenant_id: str = Header("default_tenant", alias="X-Tenant-ID"),
    mgr: ContinuousAssuranceManager = Depends(get_assurance_manager),
):
    obs = mgr.record_observation(
        tenant_id=x_tenant_id,
        source_domain=req.source_domain,
        observation_type=req.observation_type,
        payload=req.payload,
        severity=req.severity,
    )
    return ObservationResponse(
        observation_id=obs.observation_id,
        tenant_id=obs.tenant_id,
        source_domain=obs.source_domain,
        observation_type=obs.observation_type.value,
        severity=obs.severity.value,
        status=obs.status.value,
        observed_at=obs.observed_at,
    )


@router.get("/observations/{observation_id}", response_model=ObservationResponse)
def get_observation(
    observation_id: str,
    x_tenant_id: str = Header("default_tenant", alias="X-Tenant-ID"),
    mgr: ContinuousAssuranceManager = Depends(get_assurance_manager),
):
    obs = mgr.get_observation(tenant_id=x_tenant_id, observation_id=observation_id)
    return ObservationResponse(
        observation_id=obs.observation_id,
        tenant_id=obs.tenant_id,
        source_domain=obs.source_domain,
        observation_type=obs.observation_type.value,
        severity=obs.severity.value,
        status=obs.status.value,
        observed_at=obs.observed_at,
    )


# Assessments
@router.post("/assessments", response_model=AssessmentResponse)
def evaluate_assessment(
    req: AssessmentRequest,
    x_tenant_id: str = Header("default_tenant", alias="X-Tenant-ID"),
    mgr: ContinuousAssuranceManager = Depends(get_assurance_manager),
):
    ass = mgr.evaluate_tenant_assurance(tenant_id=x_tenant_id, scope=req.scope)
    return AssessmentResponse(
        assessment_id=ass.assessment_id,
        tenant_id=ass.tenant_id,
        overall_score=ass.score.overall_score,
        state=ass.state.value,
        findings_count=len(ass.findings),
        created_at=ass.created_at,
    )


@router.get("/assessments/current", response_model=AssessmentResponse)
def get_current_assessment(
    x_tenant_id: str = Header("default_tenant", alias="X-Tenant-ID"),
    mgr: ContinuousAssuranceManager = Depends(get_assurance_manager),
):
    ass = mgr.get_latest_assessment(tenant_id=x_tenant_id)
    if not ass:
        ass = mgr.evaluate_tenant_assurance(tenant_id=x_tenant_id)
    return AssessmentResponse(
        assessment_id=ass.assessment_id,
        tenant_id=ass.tenant_id,
        overall_score=ass.score.overall_score,
        state=ass.state.value,
        findings_count=len(ass.findings),
        created_at=ass.created_at,
    )


# Drift
@router.post("/drift/analyze", response_model=DriftResponse)
def analyze_drift(
    req: DriftAnalysisRequest,
    x_tenant_id: str = Header("default_tenant", alias="X-Tenant-ID"),
    mgr: ContinuousAssuranceManager = Depends(get_assurance_manager),
):
    drift = mgr.analyze_drift(
        tenant_id=x_tenant_id,
        drift_type=req.drift_type,
        expected_state=req.expected_state,
        observed_state=req.observed_state,
    )
    return DriftResponse(
        drift_id=drift.drift_id,
        tenant_id=drift.tenant_id,
        drift_type=drift.drift_type.value,
        severity=drift.severity.value,
        difference_summary=drift.difference_summary,
        confidence=drift.confidence,
        status=drift.status.value,
        detected_at=drift.detected_at,
    )


# Controls
@router.post("/controls/evaluate", response_model=ControlEvaluationResponse)
def evaluate_control(
    req: ControlEvaluationRequest,
    x_tenant_id: str = Header("default_tenant", alias="X-Tenant-ID"),
    mgr: ContinuousAssuranceManager = Depends(get_assurance_manager),
):
    ctrl = mgr.evaluate_control(tenant_id=x_tenant_id, control_id=req.control_id)
    return ControlEvaluationResponse(
        assessment_id=ctrl.assessment_id,
        tenant_id=ctrl.tenant_id,
        control_id=ctrl.control_id,
        status=ctrl.status.value,
        score=ctrl.score,
        evaluated_at=ctrl.evaluated_at,
    )


# Verification
@router.post("/verify", response_model=VerificationResponse)
def verify_resource(
    req: VerificationRequestSchema,
    x_tenant_id: str = Header("default_tenant", alias="X-Tenant-ID"),
    mgr: ContinuousAssuranceManager = Depends(get_assurance_manager),
):
    ver = mgr.verify_resource(
        tenant_id=x_tenant_id,
        target_resource_id=req.target_resource_id,
        expected_hash=req.expected_hash,
        actual_hash=req.actual_hash,
    )
    return VerificationResponse(
        verification_id=ver.verification_id,
        tenant_id=ver.tenant_id,
        target_resource_id=ver.target_resource_id,
        status=ver.status.value,
        verified_at=ver.verified_at,
    )


# Recommendations
@router.post("/recommendations", response_model=RecommendationResponse)
def create_recommendation(
    req: RecommendationRequest,
    x_tenant_id: str = Header("default_tenant", alias="X-Tenant-ID"),
    mgr: ContinuousAssuranceManager = Depends(get_assurance_manager),
):
    rec = mgr.create_recommendation(
        tenant_id=x_tenant_id,
        target_control=req.target_control,
        action_description=req.action_description,
    )
    return RecommendationResponse(
        recommendation_id=rec.recommendation_id,
        tenant_id=rec.tenant_id,
        target_control=rec.target_control,
        action_description=rec.action_description,
        priority=rec.priority,
        confidence=rec.confidence,
        auto_execute=rec.auto_execute,
        created_at=rec.created_at,
    )


# Governance
@router.post("/governance/evaluate", response_model=GovernanceEvaluationResponse)
def evaluate_governance(
    req: GovernanceEvaluationRequest,
    x_tenant_id: str = Header("default_tenant", alias="X-Tenant-ID"),
    mgr: ContinuousAssuranceManager = Depends(get_assurance_manager),
):
    res = mgr.evaluate_governance(tenant_id=x_tenant_id, action_type=req.action_type, risk_level=req.risk_level)
    return GovernanceEvaluationResponse(**res)


# Delegations
@router.post("/delegations", response_model=DelegationResponse)
def create_delegation(
    req: DelegationRequestSchema,
    x_tenant_id: str = Header("default_tenant", alias="X-Tenant-ID"),
    mgr: ContinuousAssuranceManager = Depends(get_assurance_manager),
):
    res = mgr.create_delegation(tenant_id=x_tenant_id, action_name=req.action_name, parameters=req.parameters)
    return DelegationResponse(
        delegation_id=res["delegation_id"],
        tenant_id=res["tenant_id"],
        action_name=res["action_name"],
        status=res["status"],
        created_at=datetime.now(timezone.utc),
    )


# Analytics
@router.get("/analytics")
def get_analytics(
    x_tenant_id: str = Header("default_tenant", alias="X-Tenant-ID"),
    mgr: ContinuousAssuranceManager = Depends(get_assurance_manager),
):
    return mgr.analytics.generate_report(tenant_id=x_tenant_id)
