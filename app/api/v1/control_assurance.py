"""REST API Router for Enterprise AI Control Assurance (Phase 5.38)."""

from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Query

from app.control_assurance.controls import ControlCategory, ControlCriticality
from app.control_assurance.exceptions import ControlAssuranceException
from app.control_assurance.manager import ControlAssuranceManager

router = APIRouter(prefix="/v1/control-assurance", tags=["Control Assurance"])

_global_assurance_manager = ControlAssuranceManager()


def get_assurance_manager() -> ControlAssuranceManager:
    return _global_assurance_manager


@router.get("/controls")
def list_controls(
    tenant_id: str = Header(..., alias="X-Tenant-ID"),
    category: Optional[str] = Query(None),
    mgr: ControlAssuranceManager = Depends(get_assurance_manager),
):
    """List registered controls for tenant."""
    try:
        cat_enum = ControlCategory(category) if category else None
        ctrls = mgr.control_manager.list_controls(tenant_id, category=cat_enum)
        return [c.dict() for c in ctrls]
    except ControlAssuranceException as exc:
        raise HTTPException(status_code=400, detail=exc.message)


@router.post("/controls")
def register_control(
    code: str,
    name: str,
    description: str,
    category: str = Query("SECURITY"),
    criticality: str = Query("HIGH"),
    tenant_id: str = Header(..., alias="X-Tenant-ID"),
    mgr: ControlAssuranceManager = Depends(get_assurance_manager),
):
    """Register a new enterprise control."""
    try:
        ctrl = mgr.control_manager.register_control(
            tenant_id=tenant_id,
            code=code,
            name=name,
            description=description,
            category=ControlCategory(category),
            criticality=ControlCriticality(criticality),
        )
        return ctrl.dict()
    except ControlAssuranceException as exc:
        raise HTTPException(status_code=400, detail=exc.message)


@router.get("/controls/{id}")
def get_control(
    id: str,
    tenant_id: str = Header(..., alias="X-Tenant-ID"),
    mgr: ControlAssuranceManager = Depends(get_assurance_manager),
):
    """Get control by ID."""
    try:
        ctrl = mgr.control_manager.get_control(id, tenant_id)
        return ctrl.dict()
    except ControlAssuranceException as exc:
        raise HTTPException(status_code=400, detail=exc.message)


@router.post("/controls/{id}/evaluate")
def evaluate_control(
    id: str,
    scope_target_id: str = Query("InferenceEngine_Core"),
    tenant_id: str = Header(..., alias="X-Tenant-ID"),
    mgr: ControlAssuranceManager = Depends(get_assurance_manager),
):
    """Evaluate control for target scope."""
    try:
        eval_res = mgr.evaluation_manager.evaluate_control(tenant_id, id, scope_target_id)
        return eval_res.dict()
    except ControlAssuranceException as exc:
        raise HTTPException(status_code=400, detail=exc.message)


@router.get("/evaluations")
def list_evaluations(
    tenant_id: str = Header(..., alias="X-Tenant-ID"),
    mgr: ControlAssuranceManager = Depends(get_assurance_manager),
):
    """Get control evaluation status."""
    try:
        return {"status": "ACTIVE", "tenant_id": tenant_id}
    except ControlAssuranceException as exc:
        raise HTTPException(status_code=400, detail=exc.message)


@router.get("/violations")
def list_violations(
    tenant_id: str = Header(..., alias="X-Tenant-ID"),
    mgr: ControlAssuranceManager = Depends(get_assurance_manager),
):
    """List control violations."""
    try:
        return {"tenant_id": tenant_id, "violations": []}
    except ControlAssuranceException as exc:
        raise HTTPException(status_code=400, detail=exc.message)


@router.get("/violations/{id}")
def get_violation(
    id: str,
    tenant_id: str = Header(..., alias="X-Tenant-ID"),
    mgr: ControlAssuranceManager = Depends(get_assurance_manager),
):
    """Get violation details."""
    try:
        viol = mgr.violation_manager.get_violation(id, tenant_id)
        return viol.dict()
    except ControlAssuranceException as exc:
        raise HTTPException(status_code=400, detail=exc.message)


@router.post("/violations/{id}/remediation")
def plan_remediation(
    id: str,
    control_id: str = Query(...),
    tenant_id: str = Header(..., alias="X-Tenant-ID"),
    mgr: ControlAssuranceManager = Depends(get_assurance_manager),
):
    """Plan delegated remediation for violation."""
    try:
        plan = mgr.remediation_manager.plan_remediation(tenant_id, id, control_id)
        return plan.dict()
    except ControlAssuranceException as exc:
        raise HTTPException(status_code=400, detail=exc.message)


@router.get("/evidence")
def get_evidence(
    tenant_id: str = Header(..., alias="X-Tenant-ID"),
    mgr: ControlAssuranceManager = Depends(get_assurance_manager),
):
    """Get control evidence bundles."""
    return {"tenant_id": tenant_id, "bundles": []}


@router.get("/attestations")
def list_attestations(
    tenant_id: str = Header(..., alias="X-Tenant-ID"),
    mgr: ControlAssuranceManager = Depends(get_assurance_manager),
):
    """List control attestations."""
    return {"tenant_id": tenant_id, "attestations": []}


@router.post("/attestations")
def create_attestation(
    control_id: str,
    scope_target_id: str = Query("InferenceEngine_Core"),
    tenant_id: str = Header(..., alias="X-Tenant-ID"),
    mgr: ControlAssuranceManager = Depends(get_assurance_manager),
):
    """Create control attestation."""
    try:
        att = mgr.attestation_manager.create_attestation(tenant_id, control_id, scope_target_id)
        return att.dict()
    except ControlAssuranceException as exc:
        raise HTTPException(status_code=400, detail=exc.message)


@router.get("/assurance")
def get_assurance(
    target_id: str = Query("InferenceEngine_Core"),
    tenant_id: str = Header(..., alias="X-Tenant-ID"),
    mgr: ControlAssuranceManager = Depends(get_assurance_manager),
):
    """Calculate enterprise assurance score."""
    try:
        ass = mgr.assurance_manager.calculate_assurance(tenant_id, target_id)
        return ass.dict()
    except ControlAssuranceException as exc:
        raise HTTPException(status_code=400, detail=exc.message)


@router.get("/analytics")
def get_analytics(
    tenant_id: str = Header(..., alias="X-Tenant-ID"),
    mgr: ControlAssuranceManager = Depends(get_assurance_manager),
):
    """Get control assurance analytics report."""
    try:
        report = mgr.analytics_engine.generate_assurance_report(tenant_id)
        return report.dict()
    except ControlAssuranceException as exc:
        raise HTTPException(status_code=400, detail=exc.message)


@router.post("/lifecycle/run")
def run_full_lifecycle(
    tenant_id: str = Header(..., alias="X-Tenant-ID"),
    mgr: ControlAssuranceManager = Depends(get_assurance_manager),
):
    """Run full end-to-end governed assurance lifecycle."""
    try:
        return mgr.run_full_assurance_lifecycle(tenant_id)
    except ControlAssuranceException as exc:
        raise HTTPException(status_code=400, detail=exc.message)
