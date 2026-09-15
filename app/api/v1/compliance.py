"""REST API Endpoints for Enterprise AI Compliance Platform (Phase 5.27)."""

from typing import Dict, Any, Optional, List
from fastapi import APIRouter, Depends, HTTPException, Header, Query, status

from app.compliance_platform.manager import CompliancePlatformManager
from app.compliance_platform.frameworks import FrameworkType
from app.compliance_platform.requirements import RequirementScope
from app.compliance_platform.controls import ControlType, ControlCategory, ControlImplementation
from app.compliance_platform.evidence import EvidenceType
from app.compliance_platform.findings import FindingStatus, FindingSeverity, FindingCategory
from app.compliance_platform.remediation import RemediationPriority
from app.compliance_platform.assurance import AssuranceConclusion
from app.compliance_platform.exceptions import (
    ComplianceFrameworkNotFoundException,
    ComplianceRequirementNotFoundException,
    ControlNotFoundException,
    EvidenceNotFoundException,
    ComplianceAssessmentException,
    ComplianceFindingException,
    ComplianceRemediationException,
    ImmutableEvidenceBundleException,
    ImmutableAssuranceReportException,
)

router = APIRouter(prefix="/v1/compliance", tags=["compliance-platform"])
mgr = CompliancePlatformManager()


def _get_tenant_id(x_tenant_id: Optional[str] = Header(None, alias="X-Tenant-ID")) -> str:
    return x_tenant_id or "global"


@router.post("/frameworks")
async def adopt_framework(
    payload: Dict[str, Any],
    tenant_id: str = Depends(_get_tenant_id),
):
    """Adopt a compliance framework."""
    fw_type = FrameworkType(payload.get("framework_type", "SOC_2"))
    name = payload.get("name", f"{fw_type.value} Framework")
    desc = payload.get("description", "Framework")
    fw = mgr.framework_manager.adopt_framework(tenant_id, fw_type, name, desc)
    return fw.model_dump()


@router.get("/frameworks")
async def list_frameworks(
    tenant_id: str = Depends(_get_tenant_id),
):
    """List compliance frameworks."""
    frameworks = mgr.framework_manager.list_frameworks(tenant_id)
    return [f.model_dump() for f in frameworks]


@router.post("/controls")
async def register_control(
    payload: Dict[str, Any],
    tenant_id: str = Depends(_get_tenant_id),
):
    """Register a compliance control."""
    code = payload.get("code", "CTRL-01")
    name = payload.get("name", "Unnamed Control")
    desc = payload.get("description", "Control")
    c_type = ControlType(payload.get("control_type", "PREVENTIVE"))
    category = ControlCategory(payload.get("category", "SECURITY"))
    impl = ControlImplementation(
        source_subsystem=payload.get("source_subsystem", "IdentitySecurityManager"),
        method_name=payload.get("method_name", "verify"),
    )
    req_ids = payload.get("requirement_ids", [])

    ctrl = mgr.control_manager.register_control(
        tenant_id=tenant_id,
        code=code,
        name=name,
        description=desc,
        control_type=c_type,
        category=category,
        implementation=impl,
        requirement_ids=req_ids,
    )
    return ctrl.model_dump()


@router.get("/controls")
async def list_controls(
    tenant_id: str = Depends(_get_tenant_id),
):
    """List controls for tenant."""
    ctrls = mgr.control_manager.list_controls(tenant_id)
    return [c.model_dump() for c in ctrls]


@router.post("/evidence/collect")
async def collect_evidence(
    payload: Dict[str, Any],
    tenant_id: str = Depends(_get_tenant_id),
):
    """Collect evidence for subject with idempotency."""
    idempotency_key = payload.get("idempotency_key")
    subject_type = payload.get("subject_type", "TENANT")
    subject_id = payload.get("subject_id", "global")
    req_types = [EvidenceType(t) for t in payload.get("required_evidence_types", ["AUDIT_EVENT"])]

    if not idempotency_key:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="idempotency_key is required.")

    result = mgr.collection_manager.collect_evidence_for_subject(
        tenant_id=tenant_id,
        idempotency_key=idempotency_key,
        subject_type=subject_type,
        subject_id=subject_id,
        required_types=req_types,
    )
    return result.model_dump()


@router.get("/evidence/{evidence_id}")
async def get_evidence(
    evidence_id: str,
    tenant_id: str = Depends(_get_tenant_id),
):
    """Get evidence details."""
    try:
        ev = mgr.evidence_manager.get_evidence(evidence_id, tenant_id)
        return ev.model_dump()
    except EvidenceNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


@router.post("/assessments")
async def run_assessment(
    payload: Dict[str, Any],
    tenant_id: str = Depends(_get_tenant_id),
):
    """Run compliance assessment."""
    fw_id = payload.get("framework_id")
    subject_id = payload.get("subject_id", "global")
    if not fw_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="framework_id is required.")

    try:
        ass = mgr.assessment_manager.run_assessment(tenant_id, fw_id, subject_id)
        return ass.model_dump()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/findings")
async def list_findings(
    tenant_id: str = Depends(_get_tenant_id),
):
    """List compliance findings."""
    findings = mgr.finding_manager.list_findings(tenant_id)
    return [f.model_dump() for f in findings]


@router.post("/findings/{finding_id}/acknowledge")
async def acknowledge_finding(
    finding_id: str,
    tenant_id: str = Depends(_get_tenant_id),
):
    """Acknowledge finding."""
    try:
        f = mgr.finding_manager.update_status(finding_id, tenant_id, FindingStatus.ACKNOWLEDGED)
        return f.model_dump()
    except ComplianceFindingException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


@router.get("/posture")
async def get_posture(
    tenant_id: str = Depends(_get_tenant_id),
):
    """Get compliance posture score."""
    posture = mgr.posture_manager.get_posture(tenant_id)
    return posture.model_dump()


@router.post("/attestations")
async def submit_attestation(
    payload: Dict[str, Any],
    tenant_id: str = Depends(_get_tenant_id),
):
    """Submit compliance attestation."""
    ctrl_id = payload.get("control_id")
    statement = payload.get("statement", "Control is operating effectively.")
    attested_by = payload.get("attested_by", "officer")

    if not ctrl_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="control_id is required.")

    att = mgr.attestation_manager.submit_attestation(tenant_id, ctrl_id, statement, attested_by)
    return att.model_dump()


@router.post("/exceptions")
async def request_exception(
    payload: Dict[str, Any],
    tenant_id: str = Depends(_get_tenant_id),
):
    """Request compliance exception."""
    req_id = payload.get("requirement_id")
    justification = payload.get("justification", "Business need")

    if not req_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="requirement_id is required.")

    exc = mgr.exception_manager.request_exception(tenant_id, req_id, justification)
    return exc.model_dump()


@router.post("/assurance")
async def generate_assurance_report(
    payload: Dict[str, Any],
    tenant_id: str = Depends(_get_tenant_id),
):
    """Generate immutable assurance report."""
    fw_id = payload.get("framework_id", "fw_global")
    conclusion = AssuranceConclusion(payload.get("conclusion", "ASSURED"))

    report = mgr.assurance_manager.generate_assurance_report(tenant_id, fw_id, conclusion)
    return report.model_dump()


@router.post("/audit-packages")
async def create_audit_package(
    payload: Dict[str, Any],
    tenant_id: str = Depends(_get_tenant_id),
):
    """Create immutable audit package."""
    fw_id = payload.get("framework_id", "fw_global")
    b_ref = payload.get("evidence_bundle_reference", "bundle_001")
    r_ref = payload.get("assurance_report_reference", "report_001")

    pkg = mgr.audit_manager.create_audit_package(tenant_id, fw_id, b_ref, r_ref)
    return pkg.model_dump()


@router.get("/analytics")
async def get_analytics(
    tenant_id: str = Depends(_get_tenant_id),
):
    """Get tenant compliance report & analytics."""
    report = mgr.analytics_engine.generate_report(tenant_id)
    return report.model_dump()


@router.delete("/users/{user_id}/data")
async def delete_user_data(user_id: str):
    """GDPR Right to Erasure (Data Deletion Endpoint)."""
    from app.compliance_platform.gdpr import GDPRService
    service = GDPRService()
    record = await service.erase_user_data(user_id)
    return record.model_dump()

