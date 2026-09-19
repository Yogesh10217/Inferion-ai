"""
REST API endpoints for Platform Hardening, Integration Audits & Certification.
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, Header, HTTPException, status

from app.platform_hardening.exceptions import CrossTenantPlatformHardeningException
from app.platform_hardening.manager import PlatformHardeningManager
from app.platform_hardening.schemas import (
    CertificationRequest,
    CertificationResponse,
    CertificationSchema,
    FindingSchema,
    GenericValidationRequest,
    GenericValidationResponse,
    IntegrationHealthResponse,
    PlatformAuditRequest,
    PlatformAuditResponse,
    PlatformHealthResponse,
    ReadinessResponse,
    RemediationResponse,
    RemediationSchema,
    SubsystemHealthSchema,
)

router = APIRouter(prefix="/v1/platform-hardening", tags=["Platform Hardening"])


def get_hardening_manager() -> PlatformHardeningManager:
    # Factory dependency fetching container instance
    from app.core.container import container

    return container.platform_hardening_manager


def extract_tenant_id(x_tenant_id: Optional[str] = Header(None, alias="X-Tenant-ID")) -> str:
    return x_tenant_id or "system"


@router.post("/audit", response_model=PlatformAuditResponse, status_code=status.HTTP_200_OK)
def trigger_platform_audit(
    req: PlatformAuditRequest,
    mgr: PlatformHardeningManager = Depends(get_hardening_manager),
):
    try:
        res = mgr.run_platform_audit(tenant_id=req.tenant_id)
        findings_schemas = [
            FindingSchema(
                finding_id=f.finding_id,
                tenant_id=f.tenant_id,
                rule_id=f.rule_id,
                title=f.title,
                description=f.description,
                severity=f.severity,
                subsystem=f.subsystem,
                affected_component=f.affected_component,
                file_path=f.file_path,
                line_number=f.line_number,
                root_cause_hypothesis=f.root_cause_hypothesis,
                remediation_suggestion=f.remediation_suggestion,
                evidence_reference=f.evidence_reference,
                created_at=f.created_at,
                metadata=f.metadata,
            )
            for f in res.findings
        ]

        rem_schemas = [
            RemediationSchema(
                remediation_id=r.remediation_id,
                tenant_id=r.tenant_id,
                finding_id=r.finding_id,
                severity=r.severity,
                subsystem=r.subsystem,
                affected_component=r.affected_component,
                root_cause_hypothesis=r.root_cause_hypothesis,
                recommendation=r.recommendation,
                risk=r.risk,
                priority=r.priority,
                requires_approval=r.requires_approval,
                auto_execute=r.auto_execute,
                created_at=r.created_at,
            )
            for r in res.remediations
        ]

        cert_schema = None
        if res.certification:
            cert_schema = CertificationSchema(
                certification_id=res.certification.certification_id,
                tenant_id=res.certification.tenant_id,
                status=res.certification.status,
                release_decision=res.certification.release_decision,
                overall_score=res.certification.overall_score,
                sha256_hash=res.certification.evidence.sha256_hash,
                audited_phases_count=res.certification.audited_phases_count,
                certified_at=res.certification.certified_at,
                details=res.certification.details,
            )

        critical_count = sum(1 for f in res.findings if f.severity.value == "CRITICAL")

        return PlatformAuditResponse(
            audit_id=res.audit_id,
            tenant_id=res.tenant_id,
            status=res.status,
            findings_count=len(res.findings),
            critical_findings_count=critical_count,
            readiness_score=res.readiness_score,
            release_decision=res.release_gate.decision if res.release_gate else "BLOCKED",
            certification_status=res.certification.status if res.certification else "FAILED",
            findings=findings_schemas,
            remediations=rem_schemas,
            certification=cert_schema,
            started_at=res.started_at,
            completed_at=res.completed_at,
        )
    except CrossTenantPlatformHardeningException:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/audit/{audit_id}", response_model=PlatformAuditResponse)
def get_audit_by_id(
    audit_id: str,
    tenant_id: str = Depends(extract_tenant_id),
    mgr: PlatformHardeningManager = Depends(get_hardening_manager),
):
    try:
        res = mgr.audit_repo.get(tenant_id, audit_id)
        if not res:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Audit not found")

        critical_count = sum(1 for f in res.findings if f.severity.value == "CRITICAL")
        return PlatformAuditResponse(
            audit_id=res.audit_id,
            tenant_id=res.tenant_id,
            status=res.status,
            findings_count=len(res.findings),
            critical_findings_count=critical_count,
            readiness_score=res.readiness_score,
            release_decision=res.release_gate.decision if res.release_gate else "BLOCKED",
            certification_status=res.certification.status if res.certification else "FAILED",
            findings=[],
            remediations=[],
            started_at=res.started_at,
            completed_at=res.completed_at,
        )
    except CrossTenantPlatformHardeningException:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")


@router.get("/findings", response_model=List[FindingSchema])
def list_findings(
    tenant_id: str = Depends(extract_tenant_id),
    mgr: PlatformHardeningManager = Depends(get_hardening_manager),
):
    findings = mgr.finding_repo.list_by_tenant(tenant_id)
    return [
        FindingSchema(
            finding_id=f.finding_id,
            tenant_id=f.tenant_id,
            rule_id=f.rule_id,
            title=f.title,
            description=f.description,
            severity=f.severity,
            subsystem=f.subsystem,
            affected_component=f.affected_component,
            file_path=f.file_path,
            line_number=f.line_number,
            root_cause_hypothesis=f.root_cause_hypothesis,
            remediation_suggestion=f.remediation_suggestion,
            evidence_reference=f.evidence_reference,
            created_at=f.created_at,
            metadata=f.metadata,
        )
        for f in findings
    ]


@router.get("/health", response_model=PlatformHealthResponse)
def get_platform_health(
    tenant_id: str = Depends(extract_tenant_id),
    mgr: PlatformHardeningManager = Depends(get_hardening_manager),
):
    summary = mgr.get_platform_health_summary(tenant_id=tenant_id)
    return PlatformHealthResponse(
        tenant_id=summary.tenant_id,
        integration_health=summary.integration_health,
        certification_status=summary.certification_status,
        release_readiness=summary.release_readiness,
        readiness_score=summary.readiness_score,
        total_findings=summary.total_findings,
        critical_findings=summary.critical_findings,
        timestamp=summary.timestamp,
    )


@router.get("/integration", response_model=IntegrationHealthResponse)
def get_integration_health(
    tenant_id: str = Depends(extract_tenant_id),
    mgr: PlatformHardeningManager = Depends(get_hardening_manager),
):
    health = mgr.health_repo.get(tenant_id)
    if not health:
        subsystems = mgr.subsystem_registry.list_all_subsystems()
        return IntegrationHealthResponse(
            overall_health="HEALTHY",
            overall_health_score=100.0,
            subsystems=[
                SubsystemHealthSchema(
                    subsystem_name=s.subsystem_name,
                    phase=s.phase,
                    status=s.status,
                    provider_name=s.provider_name,
                    sdk_available=s.sdk_available,
                    cli_available=s.cli_available,
                    health_score=s.health_score,
                )
                for s in subsystems
            ],
        )

    return IntegrationHealthResponse(
        overall_health=health.overall_health,
        overall_health_score=health.overall_health_score,
        subsystems=[
            SubsystemHealthSchema(
                subsystem_name=s.subsystem_name,
                phase=s.phase,
                status=s.status,
                provider_name=s.provider_name,
                sdk_available=s.sdk_available,
                cli_available=s.cli_available,
                health_score=s.health_score,
            )
            for s in health.subsystem_statuses
        ],
    )


@router.post("/certify", response_model=CertificationResponse)
def certify_platform(
    req: CertificationRequest,
    mgr: PlatformHardeningManager = Depends(get_hardening_manager),
):
    try:
        audit = mgr.run_platform_audit(tenant_id=req.tenant_id)
        cert = audit.certification
        return CertificationResponse(
            certification_id=cert.certification_id,
            tenant_id=cert.tenant_id,
            status=cert.status,
            release_decision=cert.release_decision,
            overall_score=cert.overall_score,
            sha256_hash=cert.evidence.sha256_hash,
            audited_phases_count=cert.audited_phases_count,
            certified_at=cert.certified_at,
            details=cert.details,
        )
    except CrossTenantPlatformHardeningException:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")


@router.get("/certification", response_model=CertificationResponse)
def get_certification(
    tenant_id: str = Depends(extract_tenant_id),
    mgr: PlatformHardeningManager = Depends(get_hardening_manager),
):
    cert = mgr.cert_repo.get_latest(tenant_id)
    if not cert:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No certification record found")
    return CertificationResponse(
        certification_id=cert.certification_id,
        tenant_id=cert.tenant_id,
        status=cert.status,
        release_decision=cert.release_decision,
        overall_score=cert.overall_score,
        sha256_hash=cert.evidence.sha256_hash,
        audited_phases_count=cert.audited_phases_count,
        certified_at=cert.certified_at,
        details=cert.details,
    )


@router.get("/readiness", response_model=ReadinessResponse)
def get_readiness_report(
    tenant_id: str = Depends(extract_tenant_id),
    mgr: PlatformHardeningManager = Depends(get_hardening_manager),
):
    findings = mgr.finding_repo.list_by_tenant(tenant_id)
    scores = mgr.readiness_engine.calculate_readiness_report(findings, tenant_id=tenant_id)
    cert = mgr.cert_repo.get_latest(tenant_id)

    return ReadinessResponse(
        tenant_id=tenant_id,
        readiness_score=scores["overall"],
        release_decision=cert.release_decision if cert else "BLOCKED",
        architecture_score=scores["architecture"],
        integration_score=scores["integration"],
        reliability_score=scores["reliability"],
        security_score=scores["security"],
        governance_score=scores["governance"],
        traceability_score=scores["traceability"],
        evidence_score=scores["evidence"],
        testing_score=scores["testing"],
        maintainability_score=scores["maintainability"],
        critical_blockers_count=sum(1 for f in findings if f.severity.value == "CRITICAL"),
    )


@router.get("/remediation", response_model=RemediationResponse)
def get_remediations(
    tenant_id: str = Depends(extract_tenant_id),
    mgr: PlatformHardeningManager = Depends(get_hardening_manager),
):
    rems = mgr.rem_repo.list_by_tenant(tenant_id)
    schemas = [
        RemediationSchema(
            remediation_id=r.remediation_id,
            tenant_id=r.tenant_id,
            finding_id=r.finding_id,
            severity=r.severity,
            subsystem=r.subsystem,
            affected_component=r.affected_component,
            root_cause_hypothesis=r.root_cause_hypothesis,
            recommendation=r.recommendation,
            risk=r.risk,
            priority=r.priority,
            requires_approval=r.requires_approval,
            auto_execute=r.auto_execute,
            created_at=r.created_at,
        )
        for r in rems
    ]
    return RemediationResponse(tenant_id=tenant_id, total_remediations=len(rems), remediations=schemas)


@router.post("/scan/stubs", response_model=GenericValidationResponse)
def scan_stubs_endpoint(
    req: GenericValidationRequest,
    mgr: PlatformHardeningManager = Depends(get_hardening_manager),
):
    res = mgr.stub_detection.scan_stubs(tenant_id=req.tenant_id)
    return GenericValidationResponse(
        tenant_id=req.tenant_id,
        is_valid=res.unclassified_stubs_count == 0,
        findings_count=len(res.findings),
        details={"scanned_files": res.total_files_scanned, "classifications": res.classifications},
    )
