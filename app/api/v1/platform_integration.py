"""FastAPI REST API Router for Platform Integration Fabric (Phase 5.58)."""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, Header, status

from app.platform_integration.manager import PlatformIntegrationManager
from app.platform_integration.schemas import (
    AssuranceResponse,
    ContextBuildRequest,
    ContextResponse,
    CorrelateRequest,
    CorrelateResponse,
    DelegationCreateRequest,
    DelegationResponse,
    InvestigationRequest,
    InvestigationResponse,
    RecommendationResponse,
    SnapshotCaptureResponse,
    VerificationRequest,
    VerificationResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1/platform-integration", tags=["Platform Integration Fabric"])

_manager_instance: Optional[PlatformIntegrationManager] = None


def get_integration_manager() -> PlatformIntegrationManager:
    global _manager_instance
    if _manager_instance is None:
        _manager_instance = PlatformIntegrationManager()
    return _manager_instance


@router.get("/metrics")
def get_metrics(mgr: PlatformIntegrationManager = Depends(get_integration_manager)):
    return mgr.observability.get_metrics()


# Context
@router.post("/context", response_model=ContextResponse, status_code=status.HTTP_201_CREATED)
def build_context(
    req: ContextBuildRequest,
    x_tenant_id: str = Header("default_tenant", alias="X-Tenant-ID"),
    mgr: PlatformIntegrationManager = Depends(get_integration_manager),
):
    ctx = mgr.build_context(x_tenant_id)
    return ContextResponse(
        context_id=ctx.context_id,
        tenant_id=ctx.tenant_id,
        active_platforms=ctx.active_platforms,
        signals_count=len(ctx.signals),
        findings_count=len(ctx.findings),
        fingerprint=ctx.fingerprint,
    )


# Correlate
@router.post("/correlate", response_model=CorrelateResponse)
def correlate_signals(
    req: CorrelateRequest,
    context_id: str,
    x_tenant_id: str = Header("default_tenant", alias="X-Tenant-ID"),
    mgr: PlatformIntegrationManager = Depends(get_integration_manager),
):
    corrs = mgr.correlate_signals(x_tenant_id, context_id, threshold=req.threshold)
    return CorrelateResponse(
        correlations_count=len(corrs),
        correlations=[
            {
                "correlation_id": c.correlation_id,
                "platforms": [p.value for p in c.source_platforms],
                "strength": c.correlation_strength,
                "is_causal": c.is_causal,
            }
            for c in corrs
        ],
    )


# Assurance
@router.get("/assurance", response_model=AssuranceResponse)
def get_assurance_posture(
    x_tenant_id: str = Header("default_tenant", alias="X-Tenant-ID"),
    mgr: PlatformIntegrationManager = Depends(get_integration_manager),
):
    posture = mgr.evaluate_assurance_posture(x_tenant_id)
    return AssuranceResponse(
        overall_score=posture.overall_score,
        confidence=posture.confidence,
        uncertainty=posture.uncertainty,
        trust_band=posture.trust_band,
        posture=posture.posture,
        degraded_platforms=posture.degraded_platforms,
    )


# Investigations
@router.post("/investigations", response_model=InvestigationResponse)
def run_investigation(
    req: InvestigationRequest,
    x_tenant_id: str = Header("default_tenant", alias="X-Tenant-ID"),
    mgr: PlatformIntegrationManager = Depends(get_integration_manager),
):
    res = mgr.run_investigation(x_tenant_id, req.root_platform, req.incident_description)
    return InvestigationResponse(
        investigation_id=res.investigation_id,
        root_platform=res.root_platform,
        traversed_platforms=res.traversed_platforms,
        conclusion=res.conclusion,
        evidence_count=len(res.evidence_bundle.collected_evidence_ids),
    )


# Recommendations
@router.get("/recommendations", response_model=RecommendationResponse)
def get_recommendations(
    x_tenant_id: str = Header("default_tenant", alias="X-Tenant-ID"),
    mgr: PlatformIntegrationManager = Depends(get_integration_manager),
):
    posture = mgr.evaluate_assurance_posture(x_tenant_id)
    recs = mgr.generate_recommendations(x_tenant_id, posture.degraded_platforms)
    return RecommendationResponse(
        recommendations=[
            {
                "recommendation_id": r.recommendation_id,
                "platform": r.target_platform.value,
                "action": r.action,
                "risk": r.risk_level.value,
                "auto_execute": r.auto_execute,
            }
            for r in recs
        ]
    )


# Delegations
@router.post("/delegations", response_model=DelegationResponse)
def create_delegation(
    req: DelegationCreateRequest,
    x_tenant_id: str = Header("default_tenant", alias="X-Tenant-ID"),
    mgr: PlatformIntegrationManager = Depends(get_integration_manager),
):
    del_req = mgr.delegate_action(
        x_tenant_id,
        req.recommendation_id,
        approval_id=req.approval_id,
        approval_token=req.approval_token,
    )
    return DelegationResponse(
        delegation_id=del_req.delegation_id,
        action=del_req.action,
        target=del_req.target.value,
        status=del_req.status.value,
    )


# Verification
@router.post("/verification", response_model=VerificationResponse)
def verify_delegation(
    req: VerificationRequest,
    x_tenant_id: str = Header("default_tenant", alias="X-Tenant-ID"),
    mgr: PlatformIntegrationManager = Depends(get_integration_manager),
):
    res = mgr.verify_delegation(x_tenant_id, req.delegation_id, req.pre_score, req.post_score, req.required_delta)
    return VerificationResponse(
        verification_id=res.verification_id,
        status=res.status.value,
        verified=res.verified,
        improvement_delta=res.improvement_delta,
    )


# Snapshots
@router.post("/snapshots", response_model=SnapshotCaptureResponse)
def capture_snapshot(
    x_tenant_id: str = Header("default_tenant", alias="X-Tenant-ID"),
    mgr: PlatformIntegrationManager = Depends(get_integration_manager),
):
    snap = mgr.capture_snapshot(x_tenant_id)
    return SnapshotCaptureResponse(
        snapshot_id=snap.snapshot_id,
        fingerprint=snap.state_fingerprint,
        score=snap.overall_assurance_score,
    )
