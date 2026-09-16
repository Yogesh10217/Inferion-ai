"""FastAPI REST API endpoints for Phase 5.50 Security Assurance platform."""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel

from app.security_assurance.assets import SecurityAssetType, SecurityCriticality
from app.security_assurance.exceptions import (
    CrossTenantSecurityAssuranceException,
    HighRiskSecurityActionRequiresApprovalException,
    SecretsExposureException,
    SecurityAssetNotFoundException,
)
from app.security_assurance.incidents import SecurityIncidentSeverity
from app.security_assurance.manager import SecurityAssuranceManager
from app.security_assurance.threats import ThreatSeverity, ThreatType
from app.security_assurance.vulnerabilities import VulnerabilitySeverity

router = APIRouter(prefix="/v1/security", tags=["Security Assurance"])

_manager = SecurityAssuranceManager()


def get_manager() -> SecurityAssuranceManager:
    return _manager


class RegisterAssetRequest(BaseModel):
    name: str
    asset_type: SecurityAssetType = SecurityAssetType.AI_MODEL
    criticality: SecurityCriticality = SecurityCriticality.MEDIUM
    location: str = "internal"
    owner: str = "security-team"
    metadata: Dict[str, Any] = {}


class RecordThreatRequest(BaseModel):
    title: str
    threat_type: ThreatType = ThreatType.PROMPT_INJECTION
    severity: ThreatSeverity = ThreatSeverity.HIGH
    target_asset_id: Optional[str] = None
    description: str = ""
    indicators: List[str] = []


class RecordVulnerabilityRequest(BaseModel):
    title: str
    severity: VulnerabilitySeverity = VulnerabilitySeverity.HIGH
    asset_id: str
    cve_id: Optional[str] = None
    cvss_score: float = 7.5
    description: str = ""
    remediation_guidance: str = ""


class CreateIncidentRequest(BaseModel):
    title: str
    severity: SecurityIncidentSeverity = SecurityIncidentSeverity.HIGH
    threat_ids: List[str] = []
    affected_asset_ids: List[str] = []
    description: str = ""
    idempotency_key: Optional[str] = None


class RegisterSecretReferenceRequest(BaseModel):
    name: str
    raw_secret_for_hashing_only: str
    asset_id: Optional[str] = None


class DelegateActionRequest(BaseModel):
    target_system: str
    action_name: str
    parameters: Dict[str, Any] = {}
    idempotency_key: Optional[str] = None


class EnforceGovernanceRequest(BaseModel):
    action: str
    target_resource_id: str
    is_high_risk: bool = False
    approved_by: Optional[str] = None


@router.post("/assets", response_model=Dict[str, Any])
def register_asset(
    req: RegisterAssetRequest,
    x_tenant_id: str = Header(default="default_tenant"),
    mgr: SecurityAssuranceManager = Depends(get_manager),
):
    asset = mgr.register_asset(
        tenant_id=x_tenant_id,
        name=req.name,
        asset_type=req.asset_type,
        criticality=req.criticality,
        location=req.location,
        owner=req.owner,
        metadata=req.metadata,
    )
    return asset.model_dump()


@router.get("/assets/{asset_id}", response_model=Dict[str, Any])
def get_asset(
    asset_id: str,
    x_tenant_id: str = Header(default="default_tenant"),
    mgr: SecurityAssuranceManager = Depends(get_manager),
):
    try:
        asset = mgr.asset_inventory.get_asset(x_tenant_id, asset_id)
        return asset.model_dump()
    except CrossTenantSecurityAssuranceException as e:
        raise HTTPException(status_code=403, detail=str(e))
    except SecurityAssetNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/posture", response_model=Dict[str, Any])
def evaluate_posture(
    x_tenant_id: str = Header(default="default_tenant"),
    mgr: SecurityAssuranceManager = Depends(get_manager),
):
    posture = mgr.evaluate_posture(x_tenant_id)
    return posture.model_dump()


@router.post("/threats", response_model=Dict[str, Any])
def record_threat(
    req: RecordThreatRequest,
    x_tenant_id: str = Header(default="default_tenant"),
    mgr: SecurityAssuranceManager = Depends(get_manager),
):
    threat = mgr.threat_store.record_threat(
        tenant_id=x_tenant_id,
        title=req.title,
        threat_type=req.threat_type,
        severity=req.severity,
        target_asset_id=req.target_asset_id,
        description=req.description,
        indicators=req.indicators,
    )
    return threat.model_dump()


@router.post("/vulnerabilities", response_model=Dict[str, Any])
def record_vulnerability(
    req: RecordVulnerabilityRequest,
    x_tenant_id: str = Header(default="default_tenant"),
    mgr: SecurityAssuranceManager = Depends(get_manager),
):
    vuln = mgr.vuln_store.record_vulnerability(
        tenant_id=x_tenant_id,
        title=req.title,
        severity=req.severity,
        asset_id=req.asset_id,
        cve_id=req.cve_id,
        cvss_score=req.cvss_score,
        description=req.description,
        remediation_guidance=req.remediation_guidance,
    )
    return vuln.model_dump()


@router.post("/incidents", response_model=Dict[str, Any])
def create_incident(
    req: CreateIncidentRequest,
    x_tenant_id: str = Header(default="default_tenant"),
    mgr: SecurityAssuranceManager = Depends(get_manager),
):
    inc = mgr.incident_manager.create_incident(
        tenant_id=x_tenant_id,
        title=req.title,
        severity=req.severity,
        threat_ids=req.threat_ids,
        affected_asset_ids=req.affected_asset_ids,
        description=req.description,
        idempotency_key=req.idempotency_key,
    )
    return inc.model_dump()


@router.post("/secrets/reference", response_model=Dict[str, Any])
def register_secret_reference(
    req: RegisterSecretReferenceRequest,
    x_tenant_id: str = Header(default="default_tenant"),
    mgr: SecurityAssuranceManager = Depends(get_manager),
):
    try:
        ref = mgr.secrets_engine.register_secret_reference(
            tenant_id=x_tenant_id,
            name=req.name,
            raw_secret_for_hashing_only=req.raw_secret_for_hashing_only,
            asset_id=req.asset_id,
        )
        return ref.model_dump()
    except SecretsExposureException as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/governance/enforce", response_model=Dict[str, Any])
def enforce_governance(
    req: EnforceGovernanceRequest,
    x_tenant_id: str = Header(default="default_tenant"),
    mgr: SecurityAssuranceManager = Depends(get_manager),
):
    try:
        mgr.governance_engine.enforce_execution(
            tenant_id=x_tenant_id,
            action=req.action,
            target_resource_id=req.target_resource_id,
            is_high_risk=req.is_high_risk,
            approved_by=req.approved_by,
        )
        return {"status": "SUCCESS", "message": "Governance enforcement passed cleanly."}
    except HighRiskSecurityActionRequiresApprovalException as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.post("/delegation", response_model=Dict[str, Any])
def delegate_action(
    req: DelegateActionRequest,
    x_tenant_id: str = Header(default="default_tenant"),
    mgr: SecurityAssuranceManager = Depends(get_manager),
):
    plan = mgr.delegation_manager.delegate_action(
        tenant_id=x_tenant_id,
        target_system=req.target_system,
        action_name=req.action_name,
        parameters=req.parameters,
        idempotency_key=req.idempotency_key,
    )
    return plan.model_dump()


@router.get("/assurance", response_model=Dict[str, Any])
def evaluate_assurance(
    x_tenant_id: str = Header(default="default_tenant"),
    mgr: SecurityAssuranceManager = Depends(get_manager),
):
    score = mgr.evaluate_assurance(x_tenant_id)
    return score.model_dump()


@router.get("/analytics", response_model=Dict[str, Any])
def get_analytics(
    x_tenant_id: str = Header(default="default_tenant"),
    mgr: SecurityAssuranceManager = Depends(get_manager),
):
    report = mgr.analytics_engine.generate_report(tenant_id=x_tenant_id)
    return report.model_dump()
