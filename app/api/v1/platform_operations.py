"""REST API Router for Enterprise AI Platform Operations."""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.governance_platform.risk import RiskLevel
from app.platform_operations.manager import PlatformOperationsManager
from app.platform_operations.remediation import RemediationStep, RemediationStrategy
from app.platform_operations.services import ServiceTier
from app.platform_operations.signals import SignalSeverity, SignalSource, SignalType
from app.platform_operations.slo import SLOType

router = APIRouter(prefix="/v1/platform-operations", tags=["Platform Operations"])

# Initialize singleton manager instance for API
mgr = PlatformOperationsManager()


class CreateServiceRequest(BaseModel):
    name: str
    tenant_id: str = "global"
    service_tier: ServiceTier = ServiceTier.TIER_1_HIGH
    description: str = ""
    owner_team: str = "platform-engineering"
    operational_contact: str = "ops@organization.com"
    resource_references: List[str] = []


class IngestSignalRequest(BaseModel):
    tenant_id: str = "global"
    source: SignalSource
    signal_type: SignalType
    message: str
    severity: SignalSeverity = SignalSeverity.INFO
    service_id: Optional[str] = None
    resource_id: Optional[str] = None
    correlation_id: Optional[str] = None
    metrics: Dict[str, float] = {}
    payload: Dict[str, Any] = {}


class CreateRemediationPlanRequest(BaseModel):
    tenant_id: str = "global"
    incident_id: str
    service_id: str
    steps: List[Dict[str, Any]]


class CreateSLORequest(BaseModel):
    tenant_id: str = "global"
    service_id: str
    name: str
    slo_type: SLOType
    target_threshold: float = 99.9
    description: str = ""


@router.get("/services")
def list_services(tenant_id: str = Query("global")):
    """List operational services for tenant."""
    return mgr.service_catalog_manager.list_services(tenant_id=tenant_id)


@router.post("/services", status_code=201)
def create_service(req: CreateServiceRequest):
    """Register a new service in the catalog."""
    svc = mgr.service_catalog_manager.register_service(
        tenant_id=req.tenant_id,
        name=req.name,
        service_tier=req.service_tier,
        description=req.description,
        owner_team=req.owner_team,
        operational_contact=req.operational_contact,
        resource_references=req.resource_references,
    )
    return svc.model_dump(mode="json")


@router.get("/services/{service_id}")
def get_service(service_id: str, tenant_id: str = Query("global")):
    """Get service details by ID."""
    try:
        svc = mgr.service_catalog_manager.get_service(service_id=service_id, tenant_id=tenant_id)
        return svc.model_dump(mode="json")
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/signals", status_code=202)
def ingest_signal(req: IngestSignalRequest):
    """Ingest an operational signal."""
    sig = mgr.signal_manager.ingest_signal(
        tenant_id=req.tenant_id,
        source=req.source,
        signal_type=req.signal_type,
        message=req.message,
        severity=req.severity,
        service_id=req.service_id,
        resource_id=req.resource_id,
        correlation_id=req.correlation_id,
        metrics=req.metrics,
        payload=req.payload,
    )
    return sig.model_dump(mode="json")


@router.get("/incidents/{incident_id}/context")
def get_incident_context(incident_id: str, tenant_id: str = Query("global")):
    """Retrieve enriched operational context for an incident."""
    try:
        ctx = mgr.incident_intelligence_engine.get_incident_context(incident_id=incident_id, tenant_id=tenant_id)
        return ctx.model_dump(mode="json")
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/incidents/{incident_id}/diagnosis")
def get_incident_diagnosis(incident_id: str, tenant_id: str = Query("global")):
    """Perform evidence-backed root cause diagnosis for an incident."""
    try:
        ctx = mgr.incident_intelligence_engine.get_incident_context(incident_id=incident_id, tenant_id=tenant_id)
        result = mgr.root_cause_analyzer.diagnose_incident(tenant_id=tenant_id, context=ctx)
        return result.model_dump(mode="json")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/remediations", status_code=201)
def create_remediation_plan(req: CreateRemediationPlanRequest):
    """Create a remediation plan."""
    steps = [
        RemediationStep(
            strategy=RemediationStrategy(s["strategy"]),
            target_resource_id=s["target_resource_id"],
            action_description=s.get("action_description", ""),
            expected_effect=s.get("expected_effect", ""),
            risk_level=RiskLevel(s.get("risk_level", "MEDIUM")),
            is_reversible=s.get("is_reversible", True),
        )
        for s in req.steps
    ]
    plan = mgr.remediation_planner.create_remediation_plan(
        tenant_id=req.tenant_id,
        incident_id=req.incident_id,
        service_id=req.service_id,
        steps=steps,
    )
    return plan.model_dump(mode="json")


@router.post("/remediations/{plan_id}/approve")
def approve_remediation_plan(plan_id: str, approver_id: str = Query("admin"), tenant_id: str = Query("global")):
    """Approve a gated remediation plan."""
    try:
        plan = mgr.remediation_planner.approve_remediation_plan(
            plan_id=plan_id, approver_id=approver_id, tenant_id=tenant_id
        )
        return plan.model_dump(mode="json")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/remediations/{plan_id}/execute")
def execute_remediation_plan(plan_id: str, tenant_id: str = Query("global")):
    """Execute an approved remediation plan."""
    try:
        plan = mgr.remediation_planner.execute_remediation_plan(plan_id=plan_id, tenant_id=tenant_id)
        return plan.model_dump(mode="json")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/remediations/{plan_id}/verify")
def verify_remediation_plan(plan_id: str, tenant_id: str = Query("global")):
    """Verify post-remediation service health & SLO recovery."""
    try:
        verif = mgr.remediation_verifier.verify_remediation(tenant_id=tenant_id, plan_id=plan_id)
        return verif.model_dump(mode="json")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/slo")
def list_slos(tenant_id: str = Query("global"), service_id: Optional[str] = Query(None)):
    """List SLO definitions."""
    return [s.model_dump(mode="json") for s in mgr.slo_manager.list_slos(tenant_id=tenant_id, service_id=service_id)]


@router.post("/slo", status_code=201)
def create_slo(req: CreateSLORequest):
    """Create a new SLO definition."""
    slo = mgr.slo_manager.create_slo(
        tenant_id=req.tenant_id,
        service_id=req.service_id,
        name=req.name,
        slo_type=req.slo_type,
        target_threshold=req.target_threshold,
        description=req.description,
    )
    return slo.model_dump(mode="json")


@router.get("/capacity")
def get_capacity(service_id: str = Query(...), tenant_id: str = Query("global")):
    """Get service capacity assessment."""
    ass = mgr.capacity_manager.get_latest_assessment(service_id=service_id, tenant_id=tenant_id)
    return ass.model_dump(mode="json")


@router.get("/analytics")
def get_analytics(tenant_id: str = Query("global")):
    """Get tenant operational reliability analytics report."""
    rep = mgr.operational_analytics_engine.generate_report(tenant_id=tenant_id)
    return rep.model_dump(mode="json")
