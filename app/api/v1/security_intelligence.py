"""REST API Router for Enterprise AI Security Intelligence Platform (Phase 5.32)."""

from typing import Any, Dict, Optional

from fastapi import APIRouter, Query
from pydantic import BaseModel

from app.security_intelligence.ai_threats import AIThreatSeverity, AIThreatType
from app.security_intelligence.assets import SecurityAssetCriticality, SecurityAssetType
from app.security_intelligence.incidents import SecurityIncidentSeverity
from app.security_intelligence.manager import SecurityIntelligenceManager
from app.security_intelligence.remediation import SecurityRemediationPriority
from app.security_intelligence.signals import SecuritySignalSeverity, SecuritySignalType
from app.security_intelligence.threats import ThreatSeverity, ThreatType
from app.security_intelligence.vulnerabilities import VulnerabilitySeverity

router = APIRouter(prefix="/v1/security", tags=["security-intelligence"])
mgr = SecurityIntelligenceManager()


class AssetRegisterRequest(BaseModel):
    name: str
    asset_type: SecurityAssetType = SecurityAssetType.MODEL_GATEWAY
    criticality: SecurityAssetCriticality = SecurityAssetCriticality.HIGH


class SignalIngestRequest(BaseModel):
    asset_id: str
    signal_type: SecuritySignalType
    severity: SecuritySignalSeverity = SecuritySignalSeverity.HIGH
    payload: Dict[str, Any] = {}


class ThreatCreateRequest(BaseModel):
    asset_id: str
    threat_type: ThreatType
    severity: ThreatSeverity = ThreatSeverity.HIGH


class AIThreatAnalyzeRequest(BaseModel):
    model_or_agent_id: str
    threat_type: AIThreatType = AIThreatType.PROMPT_INJECTION
    severity: AIThreatSeverity = AIThreatSeverity.HIGH


class VulnerabilityCreateRequest(BaseModel):
    asset_id: str
    title: str
    severity: VulnerabilitySeverity = VulnerabilitySeverity.HIGH
    cve_id: Optional[str] = None


class IncidentCreateRequest(BaseModel):
    asset_id: str
    title: str
    severity: SecurityIncidentSeverity = SecurityIncidentSeverity.SEV_1_HIGH


class RemediationPlanRequest(BaseModel):
    incident_id: str
    idempotency_key: str
    action_name: str = "REVOKE_KEY"
    priority: SecurityRemediationPriority = SecurityRemediationPriority.HIGH


@router.post("/assets", response_model=Dict[str, Any])
async def register_asset(
    req: AssetRegisterRequest,
    tenant_id: str = Query(..., description="Tenant ID"),
):
    asset = mgr.asset_manager.register_asset(
        tenant_id=tenant_id,
        name=req.name,
        asset_type=req.asset_type,
        criticality=req.criticality,
    )
    return asset.model_dump()


@router.post("/signals", response_model=Dict[str, Any])
async def ingest_signal(
    req: SignalIngestRequest,
    tenant_id: str = Query(..., description="Tenant ID"),
):
    sig = mgr.signal_manager.ingest_signal(
        tenant_id=tenant_id,
        asset_id=req.asset_id,
        signal_type=req.signal_type,
        severity=req.severity,
        payload=req.payload,
    )
    return sig.model_dump()


@router.post("/threats", response_model=Dict[str, Any])
async def create_threat(
    req: ThreatCreateRequest,
    tenant_id: str = Query(..., description="Tenant ID"),
):
    thrt = mgr.threat_manager.create_threat(
        tenant_id=tenant_id,
        asset_id=req.asset_id,
        threat_type=req.threat_type,
        severity=req.severity,
    )
    return thrt.model_dump()


@router.post("/ai-threats", response_model=Dict[str, Any])
async def analyze_ai_threat(
    req: AIThreatAnalyzeRequest,
    tenant_id: str = Query(..., description="Tenant ID"),
):
    aithrt = mgr.ai_threat_manager.analyze_ai_threat(
        tenant_id=tenant_id,
        model_or_agent_id=req.model_or_agent_id,
        threat_type=req.threat_type,
        severity=req.severity,
    )
    return aithrt.model_dump()


@router.post("/vulnerabilities", response_model=Dict[str, Any])
async def create_vulnerability(
    req: VulnerabilityCreateRequest,
    tenant_id: str = Query(..., description="Tenant ID"),
):
    vuln = mgr.vulnerability_manager.create_vulnerability(
        tenant_id=tenant_id,
        asset_id=req.asset_id,
        title=req.title,
        severity=req.severity,
        cve_id=req.cve_id,
    )
    return vuln.model_dump()


@router.post("/incidents", response_model=Dict[str, Any])
async def create_incident(
    req: IncidentCreateRequest,
    tenant_id: str = Query(..., description="Tenant ID"),
):
    inc = mgr.incident_manager.create_incident(
        tenant_id=tenant_id,
        asset_id=req.asset_id,
        title=req.title,
        severity=req.severity,
    )
    return inc.model_dump()


@router.post("/remediation/plan", response_model=Dict[str, Any])
async def plan_remediation(
    req: RemediationPlanRequest,
    tenant_id: str = Query(..., description="Tenant ID"),
):
    from app.platform_contracts.delegation import DelegationTarget
    from app.security_intelligence.remediation import SecurityRemediationAction

    action = SecurityRemediationAction(
        target_manager=DelegationTarget.PLATFORM_OPERATIONS, action_name=req.action_name, priority=req.priority
    )

    plan = mgr.remediation_manager.plan_remediation(
        tenant_id=tenant_id,
        incident_id=req.incident_id,
        idempotency_key=req.idempotency_key,
        actions=[action],
        priority=req.priority,
    )
    gov_dec = mgr.governance_engine.evaluate_remediation_governance(tenant_id, plan)
    return {"plan": plan.model_dump(), "governance_decision": gov_dec.model_dump()}


@router.get("/posture", response_model=Dict[str, Any])
async def get_posture(
    tenant_id: str = Query(..., description="Tenant ID"),
):
    post = mgr.posture_manager.calculate_posture(tenant_id=tenant_id)
    return post.model_dump()


@router.get("/analytics/report", response_model=Dict[str, Any])
async def get_analytics_report(
    tenant_id: str = Query(..., description="Tenant ID"),
):
    rep = mgr.analytics_engine.generate_report(tenant_id=tenant_id)
    return rep.model_dump()
