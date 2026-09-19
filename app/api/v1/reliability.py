"""REST API Router for Enterprise AI Reliability Platform (Phase 5.31)."""

from typing import Any, Dict

from fastapi import APIRouter, Query
from pydantic import BaseModel

from app.reliability_platform.incidents import IncidentSeverity
from app.reliability_platform.manager import ReliabilityPlatformManager
from app.reliability_platform.services import ServiceTier

router = APIRouter(prefix="/v1/reliability", tags=["reliability-platform"])
mgr = ReliabilityPlatformManager()


class ServiceCreateRequest(BaseModel):
    name: str
    tier: ServiceTier = ServiceTier.TIER_1_HIGH
    owner_team: str = "sre_team"


class SLOCreateRequest(BaseModel):
    service_id: str
    name: str
    target_percentage: float = 99.9


class IncidentCreateRequest(BaseModel):
    service_id: str
    title: str
    severity: IncidentSeverity = IncidentSeverity.SEV_1_HIGH


class RemediationPlanRequest(BaseModel):
    incident_id: str
    idempotency_key: str
    action_name: str = "RESTART_POD"
    is_high_risk: bool = False


class PostmortemCreateRequest(BaseModel):
    incident_id: str
    summary: str
    root_cause: str


@router.post("/services", response_model=Dict[str, Any])
async def register_service(
    req: ServiceCreateRequest,
    tenant_id: str = Query(..., description="Tenant ID"),
):
    svc = mgr.service_manager.register_service(
        tenant_id=tenant_id,
        name=req.name,
        tier=req.tier,
        owner_team=req.owner_team,
    )
    return svc.model_dump()


@router.post("/slos", response_model=Dict[str, Any])
async def create_slo(
    req: SLOCreateRequest,
    tenant_id: str = Query(..., description="Tenant ID"),
):
    slo = mgr.slo_manager.create_slo(
        tenant_id=tenant_id,
        service_id=req.service_id,
        name=req.name,
        target_percentage=req.target_percentage,
    )
    return slo.model_dump()


@router.post("/incidents", response_model=Dict[str, Any])
async def create_incident(
    req: IncidentCreateRequest,
    tenant_id: str = Query(..., description="Tenant ID"),
):
    inc = mgr.incident_manager.create_incident(
        tenant_id=tenant_id,
        service_id=req.service_id,
        title=req.title,
        severity=req.severity,
    )
    return inc.model_dump()


@router.post("/remediations/plan", response_model=Dict[str, Any])
async def plan_remediation(
    req: RemediationPlanRequest,
    tenant_id: str = Query(..., description="Tenant ID"),
):
    from app.platform_contracts.delegation import DelegationTarget
    from app.reliability_platform.remediation import RemediationAction, RemediationRisk

    risk = RemediationRisk.HIGH if req.is_high_risk else RemediationRisk.LOW
    action = RemediationAction(
        target_manager=DelegationTarget.PLATFORM_OPERATIONS, action_name=req.action_name, risk=risk
    )

    plan = mgr.remediation_manager.plan_remediation(
        tenant_id=tenant_id,
        incident_id=req.incident_id,
        idempotency_key=req.idempotency_key,
        actions=[action],
    )

    gov_dec = mgr.governance_engine.evaluate_remediation(tenant_id, plan)

    return {"plan": plan.model_dump(), "governance_decision": gov_dec.model_dump()}


@router.post("/postmortems", response_model=Dict[str, Any])
async def create_postmortem(
    req: PostmortemCreateRequest,
    tenant_id: str = Query(..., description="Tenant ID"),
):
    pm = mgr.postmortem_manager.create_postmortem(
        tenant_id=tenant_id,
        incident_id=req.incident_id,
        summary=req.summary,
        root_cause=req.root_cause,
    )
    return pm.model_dump()


@router.post("/postmortems/{report_id}/finalize", response_model=Dict[str, Any])
async def finalize_postmortem(
    report_id: str,
    tenant_id: str = Query(..., description="Tenant ID"),
):
    pm = mgr.postmortem_manager.finalize_postmortem(
        report_id=report_id,
        tenant_id=tenant_id,
    )
    return pm.model_dump()


@router.get("/analytics/report", response_model=Dict[str, Any])
async def get_analytics_report(
    tenant_id: str = Query(..., description="Tenant ID"),
):
    rep = mgr.analytics_engine.generate_report(tenant_id=tenant_id)
    return rep.model_dump()


# Backward Compatibility Endpoints for Phase 5.9
@router.get("/health", response_model=Dict[str, Any])
async def legacy_reliability_health():
    return {"status": "HEALTHY"}


@router.get("/circuit-breakers", response_model=Dict[str, Any])
async def legacy_circuit_breakers():
    return {"circuit_breakers": []}
