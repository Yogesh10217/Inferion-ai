"""FastAPI Router for Observability, SRE & Autonomous Operations Platform (/v1/operations/*)."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.operations.exceptions import OperationsException
from app.operations.manager import OperationsManager
from app.operations.runbooks import RunbookMode
from app.operations.slo import SLOType

router = APIRouter(prefix="/v1/operations", tags=["operations"])

_global_operations_manager = OperationsManager()


def get_operations() -> OperationsManager:
    return _global_operations_manager


# Schemas
class CreateSLOSchema(BaseModel):
    name: str
    target_percentage: float = 99.9
    tenant_id: str = "global"
    slo_type: SLOType = SLOType.AVAILABILITY


class TriggerAlertSchema(BaseModel):
    rule_name: str
    source_component: str
    summary: str
    tenant_id: str = "global"


# 1. Health & Topology Endpoints
@router.get("/health")
async def get_operations_health(mgr: OperationsManager = Depends(get_operations)):
    return {"status": "HEALTHY", "summary": mgr.get_summary()}


@router.get("/topology")
async def get_topology(tenant_id: Optional[str] = None, mgr: OperationsManager = Depends(get_operations)):
    nodes = mgr.topology_manager.list_nodes(tenant_id=tenant_id)
    return {"nodes": [n.model_dump() for n in nodes]}


# 2. SLOs & Error Budgets Endpoints
@router.get("/slos")
async def list_slos(tenant_id: Optional[str] = None, mgr: OperationsManager = Depends(get_operations)):
    slos = mgr.slo_manager.list_slos(tenant_id=tenant_id)
    return {"slos": [s.model_dump() for s in slos]}


@router.post("/slos", status_code=status.HTTP_201_CREATED)
async def create_slo(data: CreateSLOSchema, mgr: OperationsManager = Depends(get_operations)):
    slo = mgr.slo_manager.create_slo(
        name=data.name,
        target_percentage=data.target_percentage,
        tenant_id=data.tenant_id,
        slo_type=data.slo_type,
    )
    return {"status": "created", "slo": slo.model_dump()}


# 3. Alerts Endpoints
@router.get("/alerts")
async def list_alerts(tenant_id: Optional[str] = None, mgr: OperationsManager = Depends(get_operations)):
    alerts = mgr.alert_manager.list_alerts(tenant_id=tenant_id)
    return {"alerts": [a.model_dump() for a in alerts]}


@router.post("/alerts/{id}/acknowledge")
async def acknowledge_alert(id: str, mgr: OperationsManager = Depends(get_operations)):
    try:
        a = mgr.alert_manager.acknowledge_alert(id)
        return {"alert": a.model_dump()}
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Alert '{id}' not found")


@router.post("/alerts/{id}/resolve")
async def resolve_alert(id: str, mgr: OperationsManager = Depends(get_operations)):
    try:
        a = mgr.alert_manager.resolve_alert(id)
        return {"alert": a.model_dump()}
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Alert '{id}' not found")


# 4. Incidents & Root Cause Endpoints
@router.get("/incidents")
async def list_incidents(tenant_id: Optional[str] = None, mgr: OperationsManager = Depends(get_operations)):
    incidents = mgr.incident_manager.list_incidents(tenant_id=tenant_id)
    return {"incidents": [i.model_dump() for i in incidents]}


@router.get("/incidents/{id}")
async def get_incident(id: str, mgr: OperationsManager = Depends(get_operations)):
    try:
        inc = mgr.incident_manager.get_incident(id)
        return {"incident": inc.model_dump()}
    except OperationsException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get("/incidents/{id}/root-cause")
async def get_root_cause(id: str, mgr: OperationsManager = Depends(get_operations)):
    try:
        inc = mgr.incident_manager.get_incident(id)
        rca = mgr.rca_engine.analyze_incident(incident_id=id, failed_resource_id=inc.primary_resource_id or "service_gateway", tenant_id=inc.tenant_id)
        return {"root_cause_analysis": rca.model_dump()}
    except OperationsException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


# 5. Runbooks & Remediation Endpoints
@router.get("/runbooks")
async def list_runbooks(tenant_id: Optional[str] = None, mgr: OperationsManager = Depends(get_operations)):
    rbs = mgr.runbook_manager.list_runbooks(tenant_id=tenant_id)
    return {"runbooks": [r.model_dump() for r in rbs]}


@router.post("/runbooks/{id}/dry-run")
async def dry_runbook(id: str, mgr: OperationsManager = Depends(get_operations)):
    try:
        res = mgr.runbook_manager.execute_runbook(id, mode=RunbookMode.DRY_RUN)
        return {"execution": res.model_dump()}
    except OperationsException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("/runbooks/{id}/execute")
async def execute_runbook(id: str, mgr: OperationsManager = Depends(get_operations)):
    try:
        res = mgr.runbook_manager.execute_runbook(id, mode=RunbookMode.EXECUTE)
        return {"execution": res.model_dump()}
    except OperationsException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get("/remediation")
async def list_remediations(tenant_id: Optional[str] = None, mgr: OperationsManager = Depends(get_operations)):
    plans = mgr.remediation_engine.list_plans(tenant_id=tenant_id)
    return {"remediation_plans": [p.model_dump() for p in plans]}


@router.post("/remediation/{id}/approve")
async def approve_remediation(id: str, mgr: OperationsManager = Depends(get_operations)):
    try:
        plan = mgr.remediation_engine.approve_remediation(id)
        return {"remediation_plan": plan.model_dump()}
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Remediation plan '{id}' not found")


@router.post("/remediation/{id}/execute")
async def execute_remediation(id: str, mgr: OperationsManager = Depends(get_operations)):
    try:
        plan = mgr.remediation_engine.execute_remediation(id)
        return {"remediation_plan": plan.model_dump()}
    except OperationsException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


# 6. Analytics & Postmortems Endpoints
@router.get("/analytics")
async def get_analytics(tenant_id: str = "global", mgr: OperationsManager = Depends(get_operations)):
    rep = mgr.analytics_engine.generate_report(tenant_id=tenant_id)
    return {"analytics_report": rep.model_dump()}


@router.get("/postmortems")
async def list_postmortems(tenant_id: Optional[str] = None, mgr: OperationsManager = Depends(get_operations)):
    pms = mgr.postmortem_manager.list_postmortems(tenant_id=tenant_id)
    return {"postmortems": [p.model_dump() for p in pms]}
