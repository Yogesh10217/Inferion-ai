"""FastAPI REST API endpoints for Phase 5.49 Operations Assurance platform."""

from typing import Any, Dict, List

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel

from app.operations_assurance.events import OperationalEventType, OperationalSeverity
from app.operations_assurance.exceptions import (
    CrossTenantOperationsAssuranceException,
    ServiceNotFoundException,
)
from app.operations_assurance.forecasting import ForecastScenario
from app.operations_assurance.incidents import OperationalIncidentSeverity
from app.operations_assurance.manager import OperationsAssuranceManager
from app.operations_assurance.service_dependencies import DependencyCriticality, DependencyType
from app.operations_assurance.services import ServiceCriticality, ServiceTier, ServiceType

router = APIRouter(prefix="/v1/operations", tags=["Operations Assurance"])

_manager = OperationsAssuranceManager()


def get_manager() -> OperationsAssuranceManager:
    return _manager


class RegisterServiceRequest(BaseModel):
    name: str
    service_type: ServiceType = ServiceType.MICROSERVICE
    tier: ServiceTier = ServiceTier.TIER_1
    criticality: ServiceCriticality = ServiceCriticality.CRITICAL


class AddDependencyRequest(BaseModel):
    target_id: str
    dependency_type: DependencyType = DependencyType.API
    criticality: DependencyCriticality = DependencyCriticality.HIGH
    is_hard_dependency: bool = True


class RecordEventRequest(BaseModel):
    event_type: OperationalEventType = OperationalEventType.SERVICE_DEGRADATION
    summary: str
    severity: OperationalSeverity = OperationalSeverity.WARNING
    payload: Dict[str, Any] = {}


class CreateIncidentRequest(BaseModel):
    service_id: str
    title: str
    severity: OperationalIncidentSeverity = OperationalIncidentSeverity.SEV2
    summary: str = ""


class ForecastRequest(BaseModel):
    scenario: ForecastScenario = ForecastScenario.BASELINE
    horizon_days: int = 30


class CreatePlanRequest(BaseModel):
    steps: List[Dict[str, Any]] = []


@router.post("/services", response_model=Dict[str, Any])
def register_service(
    req: RegisterServiceRequest,
    x_tenant_id: str = Header(default="default_tenant"),
    mgr: OperationsAssuranceManager = Depends(get_manager),
):
    service = mgr.register_service(
        tenant_id=x_tenant_id,
        name=req.name,
        service_type=req.service_type,
        tier=req.tier,
        criticality=req.criticality,
    )
    return service.model_dump()


@router.get("/services/{service_id}", response_model=Dict[str, Any])
def get_service(
    service_id: str,
    x_tenant_id: str = Header(default="default_tenant"),
    mgr: OperationsAssuranceManager = Depends(get_manager),
):
    try:
        service = mgr.service_manager.get_service(x_tenant_id, service_id)
        return service.model_dump()
    except CrossTenantOperationsAssuranceException as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ServiceNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/services/{service_id}/health", response_model=Dict[str, Any])
def get_service_health(
    service_id: str,
    x_tenant_id: str = Header(default="default_tenant"),
    mgr: OperationsAssuranceManager = Depends(get_manager),
):
    try:
        health = mgr.health_manager.get_health(x_tenant_id, service_id)
        return health.model_dump()
    except CrossTenantOperationsAssuranceException as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.post("/services/{service_id}/dependencies", response_model=Dict[str, Any])
def add_dependency(
    service_id: str,
    req: AddDependencyRequest,
    x_tenant_id: str = Header(default="default_tenant"),
    mgr: OperationsAssuranceManager = Depends(get_manager),
):
    dep = mgr.dependency_manager.add_dependency(
        tenant_id=x_tenant_id,
        source_service_id=service_id,
        target_id=req.target_id,
        dependency_type=req.dependency_type,
        criticality=req.criticality,
        is_hard_dependency=req.is_hard_dependency,
    )
    mgr.dependency_graph.add_edge(x_tenant_id, service_id, req.target_id)
    return dep.model_dump()


@router.get("/services/{service_id}/dependencies", response_model=List[Dict[str, Any]])
def list_dependencies(
    service_id: str,
    x_tenant_id: str = Header(default="default_tenant"),
    mgr: OperationsAssuranceManager = Depends(get_manager),
):
    deps = mgr.dependency_manager.list_dependencies_for_service(x_tenant_id, service_id)
    return [d.model_dump() for d in deps]


@router.post("/services/{service_id}/events", response_model=Dict[str, Any])
def record_event(
    service_id: str,
    req: RecordEventRequest,
    x_tenant_id: str = Header(default="default_tenant"),
    mgr: OperationsAssuranceManager = Depends(get_manager),
):
    evt = mgr.event_manager.record_event(
        tenant_id=x_tenant_id,
        service_id=service_id,
        event_type=req.event_type,
        summary=req.summary,
        severity=req.severity,
        payload=req.payload,
    )
    return evt.model_dump()


@router.get("/services/{service_id}/reliability", response_model=Dict[str, Any])
def get_reliability(
    service_id: str,
    x_tenant_id: str = Header(default="default_tenant"),
    mgr: OperationsAssuranceManager = Depends(get_manager),
):
    assessment = mgr.reliability_engine.assess_reliability(x_tenant_id, service_id)
    return assessment.model_dump()


@router.get("/services/{service_id}/assurance", response_model=Dict[str, Any])
def get_assurance(
    service_id: str,
    x_tenant_id: str = Header(default="default_tenant"),
    mgr: OperationsAssuranceManager = Depends(get_manager),
):
    try:
        score = mgr.evaluate_assurance(x_tenant_id, service_id)
        return score.model_dump()
    except CrossTenantOperationsAssuranceException as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.post("/incidents", response_model=Dict[str, Any])
def create_incident(
    req: CreateIncidentRequest,
    x_tenant_id: str = Header(default="default_tenant"),
    mgr: OperationsAssuranceManager = Depends(get_manager),
):
    inc = mgr.incident_manager.create_incident(
        tenant_id=x_tenant_id,
        service_id=req.service_id,
        title=req.title,
        severity=req.severity,
        summary=req.summary,
    )
    return inc.model_dump()


@router.get("/analytics", response_model=Dict[str, Any])
def get_analytics(
    x_tenant_id: str = Header(default="default_tenant"),
    mgr: OperationsAssuranceManager = Depends(get_manager),
):
    report = mgr.analytics_engine.generate_report(tenant_id=x_tenant_id)
    return report.model_dump()
