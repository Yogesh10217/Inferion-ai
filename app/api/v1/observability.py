"""Enterprise AI Observability & Operations REST API Router."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Query, status
from pydantic import BaseModel, Field

from app.observability.context import ObservabilityContext
from app.observability.exceptions import (
    AlertConfigurationException,
    ExecutionNotFoundException,
    ReplayNotAvailableException,
    SLAValidationException,
    TraceNotFoundException,
)
from app.observability.manager import ObservabilityManager

router = APIRouter(tags=["Observability & Operations"])

# Global ObservabilityManager singleton instance
_observability_manager = ObservabilityManager()


def get_observability_manager() -> ObservabilityManager:
    """FastAPI Dependency for ObservabilityManager."""
    return _observability_manager


def get_request_context(
    x_tenant_id: Optional[str] = Header(default="default_tenant", alias="X-Tenant-Id"),
    x_organization_id: Optional[str] = Header(default="default_org", alias="X-Organization-Id"),
    x_workspace_id: Optional[str] = Header(default="default_workspace", alias="X-Workspace-Id"),
    x_user_id: Optional[str] = Header(default=None, alias="X-User-Id"),
) -> ObservabilityContext:
    """Dependency injecting tenant and user context."""
    return ObservabilityContext(
        tenant_id=x_tenant_id,
        organization_id=x_organization_id,
        workspace_id=x_workspace_id,
        user_id=x_user_id,
    )


# Request Schemas
class ReplayExecutionRequest(BaseModel):
    force_external_effects: bool = Field(
        default=False, description="Disables safe replay mode to repeat external side effects."
    )


class CreateSLORequest(BaseModel):
    slo_id: str
    name: str
    target_component: str
    metric_name: str
    comparator: str = Field(description="Allowed: <=, >=, <, >")
    target_value: float
    warning_threshold: Optional[float] = None
    window_seconds: int = 3600


class AcknowledgeAlertRequest(BaseModel):
    user_id: str = Field(default="system")


# --- Endpoints ---


@router.get("/v1/observability/traces", response_model=Dict[str, Any])
async def list_traces(
    manager: ObservabilityManager = Depends(get_observability_manager),
    context: ObservabilityContext = Depends(get_request_context),
):
    """Retrieve traces summary."""
    active_traces = list(manager.tracing._traces.keys())
    return {
        "tenant_id": context.tenant_id,
        "count": len(active_traces),
        "trace_ids": active_traces,
    }


@router.get("/v1/observability/traces/{trace_id}", response_model=Dict[str, Any])
async def get_trace(
    trace_id: str,
    manager: ObservabilityManager = Depends(get_observability_manager),
):
    """Retrieve detailed spans for a trace ID."""
    try:
        spans = manager.tracing.get_trace(trace_id)
        return {"trace_id": trace_id, "spans_count": len(spans), "spans": spans}
    except TraceNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/v1/observability/executions/{execution_id}", response_model=Dict[str, Any])
async def get_execution(
    execution_id: str,
    manager: ObservabilityManager = Depends(get_observability_manager),
):
    """Retrieve execution trace spans."""
    spans = manager.tracing.get_execution_trace(execution_id)
    if not spans:
        raise HTTPException(status_code=404, detail=f"Execution '{execution_id}' not found.")
    return {"execution_id": execution_id, "spans_count": len(spans), "spans": spans}


@router.get("/v1/observability/executions/{execution_id}/timeline", response_model=Dict[str, Any])
async def get_execution_timeline(
    execution_id: str,
    manager: ObservabilityManager = Depends(get_observability_manager),
):
    """Generate chronological timeline graph for an execution."""
    spans = manager.tracing.get_execution_trace(execution_id)
    if not spans:
        raise HTTPException(status_code=404, detail=f"Execution '{execution_id}' not found.")
    trace_id = spans[0].get("trace_id", execution_id)
    return manager.get_execution_timeline(trace_id)


@router.post("/v1/observability/executions/{execution_id}/replay", response_model=Dict[str, Any])
async def replay_execution(
    execution_id: str,
    req: ReplayExecutionRequest,
    manager: ObservabilityManager = Depends(get_observability_manager),
    context: ObservabilityContext = Depends(get_request_context),
):
    """Replay an execution using saved snapshot parameters."""
    try:
        res = await manager.replay_manager.replay_execution(
            execution_id=execution_id,
            force_external_effects=req.force_external_effects,
            tenant_id=context.tenant_id,
        )
        return res
    except (ExecutionNotFoundException, ReplayNotAvailableException) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/v1/observability/costs", response_model=Dict[str, Any])
async def get_costs(
    execution_id: Optional[str] = Query(None),
    agent_id: Optional[str] = Query(None),
    workflow_id: Optional[str] = Query(None),
    manager: ObservabilityManager = Depends(get_observability_manager),
    context: ObservabilityContext = Depends(get_request_context),
):
    """Retrieve cost aggregations."""
    if execution_id:
        return manager.cost_tracker.get_execution_cost(execution_id)
    elif agent_id:
        return manager.cost_tracker.get_agent_cost(agent_id)
    elif workflow_id:
        return manager.cost_tracker.get_workflow_cost(workflow_id)
    return manager.cost_tracker.get_tenant_cost(context.tenant_id or "default")


@router.get("/v1/observability/costs/breakdown", response_model=Dict[str, Any])
async def get_cost_breakdown(
    manager: ObservabilityManager = Depends(get_observability_manager),
    context: ObservabilityContext = Depends(get_request_context),
):
    """Retrieve multi-level cost attribution hierarchy."""
    return manager.cost_tracker.get_cost_breakdown(
        tenant_id=context.tenant_id,
        workspace_id=context.workspace_id,
    )


@router.get("/v1/observability/performance", response_model=Dict[str, Any])
async def get_performance(
    component: Optional[str] = Query(None),
    manager: ObservabilityManager = Depends(get_observability_manager),
):
    """Retrieve p50, p95, p99 latency percentiles and throughput."""
    if component:
        summary = manager.performance.get_component_performance(component)
        return {
            "component": summary.component,
            "count": summary.count,
            "p50_ms": summary.p50_ms,
            "p95_ms": summary.p95_ms,
            "p99_ms": summary.p99_ms,
            "avg_ms": summary.avg_ms,
            "error_rate": summary.error_rate,
            "throughput_per_sec": summary.throughput_per_sec,
        }
    return manager.performance.get_all_performance()


@router.get("/v1/observability/failures", response_model=Dict[str, Any])
async def get_failures(
    execution_id: str = Query(...),
    manager: ObservabilityManager = Depends(get_observability_manager),
):
    """Perform root cause analysis on a failed execution."""
    spans = manager.tracing.get_execution_trace(execution_id)
    report = manager.failure_analyzer.analyze_failure(execution_id, spans)
    return report.to_dict()


@router.get("/v1/observability/anomalies", response_model=List[Dict[str, Any]])
async def get_anomalies(
    limit: int = Query(50),
    manager: ObservabilityManager = Depends(get_observability_manager),
):
    """Retrieve recent statistical anomaly events."""
    return manager.anomaly_detector.get_recent_anomalies(limit=limit)


@router.get("/v1/observability/alerts", response_model=List[Dict[str, Any]])
async def get_alerts(
    status_filter: Optional[str] = Query(None, alias="status"),
    level_filter: Optional[str] = Query(None, alias="level"),
    manager: ObservabilityManager = Depends(get_observability_manager),
    context: ObservabilityContext = Depends(get_request_context),
):
    """Retrieve system alerts."""
    return manager.alert_manager.get_alerts(
        status=status_filter,
        level=level_filter,
        tenant_id=context.tenant_id,
    )


@router.post("/v1/observability/alerts/{id}/acknowledge", response_model=Dict[str, Any])
async def acknowledge_alert(
    id: str,
    req: AcknowledgeAlertRequest,
    manager: ObservabilityManager = Depends(get_observability_manager),
):
    """Acknowledge an active alert."""
    try:
        alert = manager.alert_manager.acknowledge_alert(id, user_id=req.user_id)
        return alert.to_dict()
    except AlertConfigurationException as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/v1/observability/slos", response_model=List[Dict[str, Any]])
async def get_slos(
    manager: ObservabilityManager = Depends(get_observability_manager),
    context: ObservabilityContext = Depends(get_request_context),
):
    """Retrieve Service Level Objectives status."""
    return manager.sla_engine.get_all_slo_statuses(tenant_id=context.tenant_id)


@router.post("/v1/observability/slos", response_model=Dict[str, Any])
async def create_slo(
    req: CreateSLORequest,
    manager: ObservabilityManager = Depends(get_observability_manager),
    context: ObservabilityContext = Depends(get_request_context),
):
    """Create a new SLO rule."""
    try:
        slo = manager.sla_engine.create_slo(
            slo_id=req.slo_id,
            name=req.name,
            target_component=req.target_component,
            metric_name=req.metric_name,
            comparator=req.comparator,
            target_value=req.target_value,
            warning_threshold=req.warning_threshold,
            window_seconds=req.window_seconds,
            tenant_id=context.tenant_id,
            workspace_id=context.workspace_id,
        )
        return slo.to_dict()
    except SLAValidationException as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/v1/observability/evaluations", response_model=List[Dict[str, Any]])
async def get_evaluations(
    manager: ObservabilityManager = Depends(get_observability_manager),
):
    """Retrieve Quality & Evaluation scores."""
    return [e.to_dict() for e in manager.evaluation_engine._evaluations]


@router.get("/v1/operations/status", response_model=Dict[str, Any])
async def get_operations_status(
    manager: ObservabilityManager = Depends(get_observability_manager),
):
    """Retrieve overall platform operational status."""
    return manager.get_operations_status()


@router.get("/v1/operations/dashboard", response_model=Dict[str, Any])
async def get_operations_dashboard(
    manager: ObservabilityManager = Depends(get_observability_manager),
    context: ObservabilityContext = Depends(get_request_context),
):
    """Retrieve executive operations dashboard data."""
    return manager.get_operations_dashboard(tenant_id=context.tenant_id)
