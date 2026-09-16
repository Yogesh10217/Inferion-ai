"""REST API Endpoints for Operations Intelligence Platform (Phase 5.41)."""

from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel

from app.operations_intelligence.exceptions import (
    CrossTenantOperationsAccessException,
)
from app.operations_intelligence.manager import OperationsIntelligenceManager

router = APIRouter(prefix="/v1/operations", tags=["Operations Intelligence"])
_mgr = OperationsIntelligenceManager()


class ServiceCreateRequest(BaseModel):
    tenant_id: str
    name: str
    owner_team: str
    criticality: str = "BUSINESS_CRITICAL"
    tier: str = "TIER_1"


class AlertIngestRequest(BaseModel):
    tenant_id: str
    source_system: str
    service_id: str
    alert_name: str
    fingerprint: str
    severity: str = "HIGH"


class IncidentCreateRequest(BaseModel):
    tenant_id: str
    title: str
    affected_service_id: str
    severity: str = "P2_HIGH"
    priority: str = "P2"


class MajorIncidentDeclareRequest(BaseModel):
    tenant_id: str
    incident_id: str
    title: str
    impact: str = "CRITICAL_BUSINESS_HALT"


class RemediationPlanRequest(BaseModel):
    tenant_id: str
    incident_id: str
    idempotency_key: str
    actions: List[Dict[str, Any]]
    requires_approval: bool = False


@router.post("/services", status_code=status.HTTP_201_CREATED)
def register_service(req: ServiceCreateRequest) -> Dict[str, Any]:
    svc = _mgr.service_manager.register_service(
        tenant_id=req.tenant_id,
        name=req.name,
        owner_team=req.owner_team,
        criticality=req.criticality,  # type: ignore
        tier=req.tier,  # type: ignore
    )
    _mgr.service_repo.save(svc)
    return svc.model_dump(mode="json")


@router.get("/services")
def list_services(tenant_id: str = Query(..., description="Tenant ID")) -> List[Dict[str, Any]]:
    return [s.model_dump(mode="json") for s in _mgr.service_repo.list(tenant_id)]


@router.post("/alerts/ingest", status_code=status.HTTP_201_CREATED)
def ingest_alert(req: AlertIngestRequest) -> Dict[str, Any]:
    alt = _mgr.alert_manager.ingest_alert(
        tenant_id=req.tenant_id,
        source_system=req.source_system,
        service_id=req.service_id,
        alert_name=req.alert_name,
        fingerprint=req.fingerprint,
        severity=req.severity,  # type: ignore
    )
    _mgr.alert_repo.save(alt)
    return alt.model_dump(mode="json")


@router.get("/alerts")
def list_alerts(tenant_id: str = Query(..., description="Tenant ID")) -> List[Dict[str, Any]]:
    return [a.model_dump(mode="json") for a in _mgr.alert_repo.list(tenant_id)]


@router.post("/incidents", status_code=status.HTTP_201_CREATED)
def create_incident(req: IncidentCreateRequest) -> Dict[str, Any]:
    inc = _mgr.incident_manager.create_incident(
        tenant_id=req.tenant_id,
        title=req.title,
        affected_service_id=req.affected_service_id,
        severity=req.severity,  # type: ignore
        priority=req.priority,  # type: ignore
    )
    _mgr.incident_repo.save(inc)
    return inc.model_dump(mode="json")


@router.get("/incidents")
def list_incidents(tenant_id: str = Query(..., description="Tenant ID")) -> List[Dict[str, Any]]:
    return [i.model_dump(mode="json") for i in _mgr.incident_repo.list(tenant_id)]


@router.post("/major-incidents/declare", status_code=status.HTTP_201_CREATED)
def declare_major_incident(req: MajorIncidentDeclareRequest) -> Dict[str, Any]:
    try:
        maj = _mgr.major_incident_manager.declare_major_incident(
            tenant_id=req.tenant_id,
            incident_id=req.incident_id,
            title=req.title,
            impact=req.impact,  # type: ignore
        )
        _mgr.major_incident_repo.save(maj)
        return maj.model_dump(mode="json")
    except CrossTenantOperationsAccessException:
        raise HTTPException(status_code=403, detail="Access denied.")


@router.get("/analytics")
def get_analytics(tenant_id: str = Query(..., description="Tenant ID")) -> Dict[str, Any]:
    rpt = _mgr.analytics_engine.generate_report(tenant_id)
    return rpt.model_dump(mode="json")
