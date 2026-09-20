"""
FastAPI REST API endpoints for Phase 5.51 Enterprise AI Unified Intelligence Platform.
"""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel, Field

from app.unified_intelligence.domains import IntelligenceDomain
from app.unified_intelligence.exceptions import (
    HighRiskUnifiedActionRequiresApprovalException,
    InvalidUnifiedIntelligenceInputException,
)
from app.unified_intelligence.manager import UnifiedIntelligenceManager
from app.unified_intelligence.normalization_contracts import UnifiedDomainInput

router = APIRouter(prefix="/intelligence", tags=["Unified Intelligence"])

_manager = UnifiedIntelligenceManager()


def get_manager() -> UnifiedIntelligenceManager:
    return _manager


class IngestSignalRequest(BaseModel):
    domain: str
    entity_reference: str
    signal_type: str
    severity: str = "MEDIUM"
    confidence_score: float = 0.85
    risk_score: float = 0.5
    evidence_references: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    idempotency_key: Optional[str] = None


class EvaluateGovernanceRequest(BaseModel):
    recommendation_id: str
    approved_by: Optional[str] = None


class ExecuteDelegationRequest(BaseModel):
    plan_id: str
    step_id: str
    approved_by: Optional[str] = None


class CreateInvestigationRequest(BaseModel):
    situation_id: str
    title: Optional[str] = None
    assigned_to: Optional[str] = None


@router.post("/signals", response_model=Dict[str, Any])
def ingest_signal(
    req: IngestSignalRequest,
    x_tenant_id: str = Header(default="default_tenant"),
    mgr: UnifiedIntelligenceManager = Depends(get_manager),
):
    try:
        domain_enum = IntelligenceDomain(req.domain)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid domain: {req.domain}")

    domain_input = UnifiedDomainInput(
        domain=domain_enum,
        tenant_id=x_tenant_id,
        entity_reference=req.entity_reference,
        signal_type=req.signal_type,
        severity=req.severity,
        confidence_score=req.confidence_score,
        risk_score=req.risk_score,
        evidence_references=req.evidence_references,
        metadata=req.metadata,
        idempotency_key=req.idempotency_key,
    )

    sig = mgr.ingest_domain_input(x_tenant_id, domain_input, req.idempotency_key)
    return sig.to_dict()


@router.post("/situations/evaluate", response_model=List[Dict[str, Any]])
def evaluate_situations(
    x_tenant_id: str = Header(default="default_tenant"), mgr: UnifiedIntelligenceManager = Depends(get_manager)
):
    situations = mgr.detect_situations(x_tenant_id)
    return [s.to_dict() for s in situations]


@router.get("/risk", response_model=Dict[str, Any])
def evaluate_risk(
    x_tenant_id: str = Header(default="default_tenant"), mgr: UnifiedIntelligenceManager = Depends(get_manager)
):
    risk = mgr.evaluate_risk(x_tenant_id)
    return risk.to_dict()


@router.get("/assurance", response_model=Dict[str, Any])
def evaluate_assurance(
    x_tenant_id: str = Header(default="default_tenant"), mgr: UnifiedIntelligenceManager = Depends(get_manager)
):
    assr = mgr.evaluate_assurance(x_tenant_id)
    return assr.to_dict()


@router.get("/trust/{entity_ref:path}", response_model=Dict[str, Any])
def evaluate_trust(
    entity_ref: str,
    x_tenant_id: str = Header(default="default_tenant"),
    mgr: UnifiedIntelligenceManager = Depends(get_manager),
):
    trust = mgr.evaluate_trust(x_tenant_id, entity_ref)
    return trust.to_dict()


@router.post("/recommendations/{situation_id}", response_model=List[Dict[str, Any]])
def generate_recommendations(
    situation_id: str,
    x_tenant_id: str = Header(default="default_tenant"),
    mgr: UnifiedIntelligenceManager = Depends(get_manager),
):
    try:
        recs = mgr.generate_recommendations(x_tenant_id, situation_id)
        return [r.to_dict() for r in recs]
    except InvalidUnifiedIntelligenceInputException as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/governance/evaluate", response_model=Dict[str, Any])
def evaluate_governance(
    req: EvaluateGovernanceRequest,
    x_tenant_id: str = Header(default="default_tenant"),
    mgr: UnifiedIntelligenceManager = Depends(get_manager),
):
    try:
        recs = mgr.repository.list_recommendations(x_tenant_id)
        target = next((r for r in recs if r.recommendation_id == req.recommendation_id), None)
        if not target:
            raise HTTPException(status_code=404, detail=f"Recommendation {req.recommendation_id} not found.")

        result = mgr.evaluate_governance(x_tenant_id, target, approved_by=req.approved_by)
        return result.to_dict()
    except HighRiskUnifiedActionRequiresApprovalException as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.post("/investigations", response_model=Dict[str, Any])
def create_investigation(
    req: CreateInvestigationRequest,
    x_tenant_id: str = Header(default="default_tenant"),
    mgr: UnifiedIntelligenceManager = Depends(get_manager),
):
    try:
        inv = mgr.create_investigation(x_tenant_id, req.situation_id, title=req.title, assigned_to=req.assigned_to)
        return inv.to_dict()
    except InvalidUnifiedIntelligenceInputException as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/snapshot", response_model=Dict[str, Any])
def generate_snapshot(
    x_tenant_id: str = Header(default="default_tenant"), mgr: UnifiedIntelligenceManager = Depends(get_manager)
):
    snap = mgr.generate_snapshot(x_tenant_id)
    return snap.to_dict()


@router.get("/analytics", response_model=Dict[str, Any])
def get_analytics(
    x_tenant_id: str = Header(default="default_tenant"), mgr: UnifiedIntelligenceManager = Depends(get_manager)
):
    analytics = mgr.get_analytics_summary(x_tenant_id)
    return analytics.to_dict()


@router.get("/billing", response_model=Dict[str, Any])
def get_billing(
    x_tenant_id: str = Header(default="default_tenant"), mgr: UnifiedIntelligenceManager = Depends(get_manager)
):
    bill = mgr.get_billing(x_tenant_id)
    return bill.to_dict()
