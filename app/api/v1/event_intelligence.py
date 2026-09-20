"""REST API Router for Enterprise AI Event Intelligence Platform (Phase 5.34)."""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Query
from pydantic import BaseModel

from app.event_intelligence.automation import AutomationAction
from app.event_intelligence.events import EventCategory, EventSeverity, EventType
from app.event_intelligence.manager import EventIntelligenceManager
from app.event_intelligence.resolution import EventResolutionStatus
from app.event_intelligence.response import ResponseTarget

router = APIRouter(prefix="/events", tags=["event-intelligence"])
mgr = EventIntelligenceManager()


class CreateEventRequest(BaseModel):
    source_name: str = "ExternalSystem"
    event_type: EventType = EventType.CUSTOM_EVENT
    category: EventCategory = EventCategory.OPERATIONAL
    severity: EventSeverity = EventSeverity.MEDIUM
    payload: Dict[str, Any] = {}
    idempotency_reference: Optional[str] = None


class CreateRuleRequest(BaseModel):
    name: str
    action_name: str = "REQUEST_INVESTIGATION"


class EvaluateAutomationRequest(BaseModel):
    event_id: str
    action: AutomationAction = AutomationAction.REQUEST_INVESTIGATION
    is_high_risk: bool = False


class RespondRequest(BaseModel):
    target: ResponseTarget = ResponseTarget.RELIABILITY_PLATFORM
    action_type: str = "INVESTIGATE_INCIDENT"


class ResolveRequest(BaseModel):
    target_status: EventResolutionStatus = EventResolutionStatus.RESOLVED


@router.post("", response_model=Dict[str, Any])
async def create_event(
    req: CreateEventRequest,
    tenant_id: str = Query(..., description="Tenant ID"),
):
    src = mgr.source_manager.register_source(tenant_id, req.source_name)
    evt = mgr.event_manager.create_event(
        tenant_id=tenant_id,
        source_id=src.source_id,
        source_name=src.name,
        event_type=req.event_type,
        category=req.category,
        severity=req.severity,
        payload=req.payload,
        idempotency_reference=req.idempotency_reference,
    )
    return evt.model_dump()


@router.get("", response_model=List[Dict[str, Any]])
async def list_events(
    tenant_id: str = Query(..., description="Tenant ID"),
):
    events = mgr.event_manager.list_events(tenant_id)
    return [e.model_dump() for e in events]


@router.get("/{event_id}", response_model=Dict[str, Any])
async def get_event(
    event_id: str,
    tenant_id: str = Query(..., description="Tenant ID"),
):
    evt = mgr.event_manager.get_event(event_id, tenant_id)
    return evt.model_dump()


@router.get("/correlations", response_model=List[Dict[str, Any]])
async def list_correlations(
    tenant_id: str = Query(..., description="Tenant ID"),
):
    groups = mgr.correlation_manager.list_groups(tenant_id)
    return [g.model_dump() for g in groups]


@router.get("/correlations/{correlation_id}", response_model=Dict[str, Any])
async def get_correlation(
    correlation_id: str,
    tenant_id: str = Query(..., description="Tenant ID"),
):
    grp = mgr.correlation_manager.get_group(correlation_id, tenant_id)
    return grp.model_dump()


@router.post("/automation/rules", response_model=Dict[str, Any])
async def create_automation_rule(
    req: CreateRuleRequest,
    tenant_id: str = Query(..., description="Tenant ID"),
):
    rule = mgr.rule_manager.create_rule(tenant_id, req.name)
    return rule.model_dump()


@router.get("/automation/rules", response_model=List[Dict[str, Any]])
async def list_automation_rules(
    tenant_id: str = Query(..., description="Tenant ID"),
):
    rules = mgr.rule_manager.list_rules(tenant_id)
    return [r.model_dump() for r in rules]


@router.post("/automation/evaluate", response_model=Dict[str, Any])
async def evaluate_automation(
    req: EvaluateAutomationRequest,
    tenant_id: str = Query(..., description="Tenant ID"),
):
    evt = mgr.event_manager.get_event(req.event_id, tenant_id)
    gov_dec = mgr.governance_engine.evaluate_automation_governance(
        tenant_id, req.event_id, is_high_risk=req.is_high_risk
    )
    plan = mgr.automation_manager.create_automation_plan(evt, action=req.action, requires_approval=req.is_high_risk)
    return {"governance_decision": gov_dec.model_dump(), "automation_plan": plan.model_dump()}


@router.post("/{event_id}/investigate", response_model=Dict[str, Any])
async def investigate_event(
    event_id: str,
    tenant_id: str = Query(..., description="Tenant ID"),
):
    inv = mgr.investigation_manager.initiate_investigation(tenant_id, event_id)
    return inv.model_dump()


@router.post("/{event_id}/respond", response_model=Dict[str, Any])
async def respond_to_event(
    event_id: str,
    req: RespondRequest,
    tenant_id: str = Query(..., description="Tenant ID"),
):
    from app.event_intelligence.response import EventResponseAction

    act = EventResponseAction(target=req.target, action_type=req.action_type)
    plan = mgr.response_manager.create_response_plan(tenant_id, event_id, [act])
    return plan.model_dump()


@router.post("/{event_id}/resolve", response_model=Dict[str, Any])
async def resolve_event(
    event_id: str,
    req: ResolveRequest,
    tenant_id: str = Query(..., description="Tenant ID"),
):
    res = mgr.resolution_manager.create_resolution(tenant_id, event_id)
    res = mgr.resolution_manager.transition_resolution(
        res.resolution_id, tenant_id, EventResolutionStatus.INVESTIGATING
    )
    res = mgr.resolution_manager.transition_resolution(
        res.resolution_id, tenant_id, EventResolutionStatus.RESPONSE_PLANNED
    )
    res = mgr.resolution_manager.transition_resolution(res.resolution_id, tenant_id, EventResolutionStatus.DELEGATED)
    res = mgr.resolution_manager.transition_resolution(res.resolution_id, tenant_id, EventResolutionStatus.VERIFYING)
    final_res = mgr.resolution_manager.transition_resolution(res.resolution_id, tenant_id, req.target_status)
    return final_res.model_dump()


@router.get("/analytics", response_model=Dict[str, Any])
async def get_analytics_report(
    tenant_id: str = Query(..., description="Tenant ID"),
):
    rep = mgr.analytics_engine.generate_report(tenant_id=tenant_id)
    return rep.model_dump()


@router.get("/patterns", response_model=List[Dict[str, Any]])
async def get_patterns(
    tenant_id: str = Query(..., description="Tenant ID"),
):
    events = mgr.event_manager.list_events(tenant_id)
    pats = mgr.pattern_detector.detect_patterns(tenant_id, events)
    return [p.model_dump() for p in pats]
