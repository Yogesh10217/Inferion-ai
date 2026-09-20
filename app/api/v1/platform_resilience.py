"""REST API Router for Enterprise AI Platform Resilience (Phase 5.37)."""

from fastapi import APIRouter, Depends, Header, HTTPException, Query

from app.platform_resilience.exceptions import PlatformResilienceException
from app.platform_resilience.manager import PlatformResilienceManager

router = APIRouter(prefix="/resilience", tags=["Platform Resilience"])

_global_resilience_manager = PlatformResilienceManager()


def get_resilience_manager() -> PlatformResilienceManager:
    return _global_resilience_manager


@router.post("/services/register")
def register_resilience_service(
    service_name: str,
    tenant_id: str = Header(..., alias="X-Tenant-ID"),
    tier: str = Query("TIER_2_STANDARD"),
    region: str = Query("us-east-1"),
    mgr: PlatformResilienceManager = Depends(get_resilience_manager),
):
    """Register service for resilience tracking."""
    try:
        svc = mgr.service_manager.register_service(tenant_id, service_name, region=region)
        return {"status": "registered", "service": svc.dict()}
    except PlatformResilienceException as exc:
        raise HTTPException(status_code=400, detail=exc.message)


@router.get("/capacity/evaluate")
def evaluate_capacity(
    resource_id: str,
    tenant_id: str = Header(..., alias="X-Tenant-ID"),
    mgr: PlatformResilienceManager = Depends(get_resilience_manager),
):
    """Evaluate capacity for a resource."""
    try:
        eval_res = mgr.capacity_manager.evaluate_capacity(tenant_id, resource_id)
        return eval_res.dict()
    except PlatformResilienceException as exc:
        raise HTTPException(status_code=400, detail=exc.message)


@router.post("/scaling/plan")
def plan_scaling(
    resource_id: str,
    tenant_id: str = Header(..., alias="X-Tenant-ID"),
    direction: str = Query("SCALE_OUT"),
    mgr: PlatformResilienceManager = Depends(get_resilience_manager),
):
    """Generate scaling plan and delegate execution."""
    try:
        plan = mgr.scaling_manager.plan_scaling(tenant_id, resource_id)
        return plan.dict()
    except PlatformResilienceException as exc:
        raise HTTPException(status_code=400, detail=exc.message)


@router.get("/backpressure/assess")
def assess_backpressure(
    service_id: str,
    queue_depth: int = Query(100),
    tenant_id: str = Header(..., alias="X-Tenant-ID"),
    mgr: PlatformResilienceManager = Depends(get_resilience_manager),
):
    """Assess backpressure and overload protection."""
    try:
        assessment = mgr.backpressure_manager.evaluate_backpressure(tenant_id, service_id, queue_depth)
        return assessment.dict()
    except PlatformResilienceException as exc:
        raise HTTPException(status_code=400, detail=exc.message)


@router.post("/failover/request")
def request_failover(
    service_id: str,
    source_region: str = Query("us-east-1"),
    target_region: str = Query("us-west-2"),
    tenant_id: str = Header(..., alias="X-Tenant-ID"),
    mgr: PlatformResilienceManager = Depends(get_resilience_manager),
):
    """Request controlled regional failover."""
    try:
        plan = mgr.failover_manager.create_failover_request(tenant_id, service_id, source_region, target_region)
        return plan.dict()
    except PlatformResilienceException as exc:
        raise HTTPException(status_code=400, detail=exc.message)


@router.post("/dr/activate")
def activate_disaster_recovery(
    dr_plan_id: str,
    tenant_id: str = Header(..., alias="X-Tenant-ID"),
    mgr: PlatformResilienceManager = Depends(get_resilience_manager),
):
    """Activate disaster recovery workflow."""
    try:
        plan = mgr.dr_manager.activate_dr_plan(dr_plan_id, tenant_id)
        return plan.dict()
    except PlatformResilienceException as exc:
        raise HTTPException(status_code=400, detail=exc.message)


@router.get("/readiness/assess")
def assess_readiness(
    service_id: str,
    tenant_id: str = Header(..., alias="X-Tenant-ID"),
    mgr: PlatformResilienceManager = Depends(get_resilience_manager),
):
    """Assess production readiness."""
    try:
        assessment = mgr.readiness_manager.assess_readiness(tenant_id, service_id)
        return assessment.dict()
    except PlatformResilienceException as exc:
        raise HTTPException(status_code=400, detail=exc.message)


@router.get("/analytics/report")
def get_analytics_report(
    tenant_id: str = Header(..., alias="X-Tenant-ID"),
    mgr: PlatformResilienceManager = Depends(get_resilience_manager),
):
    """Get platform resilience analytics report."""
    try:
        report = mgr.analytics_engine.generate_resilience_report(tenant_id)
        return report.dict()
    except PlatformResilienceException as exc:
        raise HTTPException(status_code=400, detail=exc.message)


@router.post("/lifecycle/run")
def run_full_lifecycle(
    tenant_id: str = Header(..., alias="X-Tenant-ID"),
    mgr: PlatformResilienceManager = Depends(get_resilience_manager),
):
    """Run full end-to-end governed resilience lifecycle."""
    try:
        return mgr.run_full_resilience_lifecycle(tenant_id)
    except PlatformResilienceException as exc:
        raise HTTPException(status_code=400, detail=exc.message)
