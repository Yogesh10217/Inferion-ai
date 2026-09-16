"""FastAPI REST API Router for Phase 5.16 Enterprise AI Governance Platform."""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from app.governance_platform.compliance import FrameworkType
from app.governance_platform.governance_manager import GovernancePlatformManager
from app.governance_platform.remediation import EnforcementAction
from app.governance_platform.risk import RiskCategory, RiskFactor
from app.governance_platform.violations import ViolationSeverity, ViolationType

router = APIRouter(prefix="/v1/governance", tags=["Governance Platform"])

_global_governance = GovernancePlatformManager()


def get_governance_manager() -> GovernancePlatformManager:
    return _global_governance


class EvaluatePolicyRequest(BaseModel):
    action: str
    resource_id: str
    tenant_id: str = "global"
    actor_id: str = "user"
    context: Dict[str, Any] = Field(default_factory=dict)


class RiskAssessRequest(BaseModel):
    target_resource_id: str
    category: RiskCategory = RiskCategory.SECURITY
    factors: List[Dict[str, Any]] = Field(default_factory=list)
    tenant_id: str = "global"


class AssessComplianceRequest(BaseModel):
    framework: FrameworkType = FrameworkType.SOC2
    tenant_id: str = "global"


class RecordViolationRequest(BaseModel):
    title: str
    violation_type: ViolationType = ViolationType.POLICY_VIOLATION
    severity: ViolationSeverity = ViolationSeverity.MEDIUM
    primary_resource_id: str
    description: str = ""
    tenant_id: str = "global"


class PlanRemediationRequest(BaseModel):
    target_resource_id: str
    action: EnforcementAction = EnforcementAction.PAUSE_RESOURCE
    tenant_id: str = "global"
    is_emergency: bool = False


@router.get("/health", status_code=status.HTTP_200_OK)
def governance_health():
    return {"status": "HEALTHY", "subsystem": "Governance Platform", "phase": "5.16"}


@router.post("/policies/evaluate", status_code=status.HTTP_200_OK)
def evaluate_policy(
    req: EvaluatePolicyRequest,
    mgr: GovernancePlatformManager = Depends(get_governance_manager),
):
    res = mgr.policy_evaluator.evaluate_request(
        action=req.action,
        resource_id=req.resource_id,
        tenant_id=req.tenant_id,
        actor_id=req.actor_id,
        context=req.context,
    )
    mgr.metrics_collector.record_evaluation(req.tenant_id, res.decision.value)
    return res.model_dump()


@router.post("/risk/assess", status_code=status.HTTP_201_CREATED)
def assess_risk(
    req: RiskAssessRequest,
    mgr: GovernancePlatformManager = Depends(get_governance_manager),
):
    factors = [RiskFactor(**f) for f in req.factors] if req.factors else []
    ass = mgr.risk_manager.calculate_risk(
        target_resource_id=req.target_resource_id,
        factors=factors,
        category=req.category,
        tenant_id=req.tenant_id,
    )
    mgr.metrics_collector.record_risk_score(req.tenant_id, ass.overall_score)
    return ass.model_dump()


@router.get("/risk", status_code=status.HTTP_200_OK)
def list_risk_assessments(
    tenant_id: Optional[str] = Query(None),
    mgr: GovernancePlatformManager = Depends(get_governance_manager),
):
    return {"assessments": [a.model_dump() for a in mgr.risk_manager.list_assessments(tenant_id)]}


@router.post("/compliance/assess", status_code=status.HTTP_201_CREATED)
def assess_compliance(
    req: AssessComplianceRequest,
    mgr: GovernancePlatformManager = Depends(get_governance_manager),
):
    ass = mgr.compliance_manager.run_assessment(framework=req.framework, tenant_id=req.tenant_id)
    return ass.model_dump()


@router.get("/compliance", status_code=status.HTTP_200_OK)
def list_compliance_assessments(
    tenant_id: Optional[str] = Query(None),
    mgr: GovernancePlatformManager = Depends(get_governance_manager),
):
    return {"assessments": [a.model_dump() for a in mgr.compliance_manager.list_assessments(tenant_id)]}


@router.get("/evidence", status_code=status.HTTP_200_OK)
def list_evidence(
    tenant_id: Optional[str] = Query(None),
    resource_id: Optional[str] = Query(None),
    mgr: GovernancePlatformManager = Depends(get_governance_manager),
):
    return {"evidence": [e.model_dump() for e in mgr.evidence_collector.list_evidence(tenant_id, resource_id)]}


@router.get("/violations", status_code=status.HTTP_200_OK)
def list_violations(
    tenant_id: Optional[str] = Query(None),
    mgr: GovernancePlatformManager = Depends(get_governance_manager),
):
    return {"violations": [v.model_dump() for v in mgr.violation_manager.list_violations(tenant_id)]}


@router.post("/violations", status_code=status.HTTP_201_CREATED)
def record_violation(
    req: RecordViolationRequest,
    mgr: GovernancePlatformManager = Depends(get_governance_manager),
):
    v = mgr.violation_manager.record_violation(
        title=req.title,
        violation_type=req.violation_type,
        severity=req.severity,
        primary_resource_id=req.primary_resource_id,
        description=req.description,
        tenant_id=req.tenant_id,
    )
    mgr.metrics_collector.record_violation(req.tenant_id, req.severity.value)
    return v.model_dump()


@router.get("/trust", status_code=status.HTTP_200_OK)
def get_trust_assessment(
    resource_id: str = Query("global_resource"),
    tenant_id: str = Query("global"),
    mgr: GovernancePlatformManager = Depends(get_governance_manager),
):
    ass = mgr.trust_engine.calculate_trust(target_resource_id=resource_id, tenant_id=tenant_id)
    return ass.model_dump()


@router.post("/remediation/plan", status_code=status.HTTP_201_CREATED)
def plan_remediation(
    req: PlanRemediationRequest,
    mgr: GovernancePlatformManager = Depends(get_governance_manager),
):
    rem = mgr.enforcement_engine.plan_remediation(
        target_resource_id=req.target_resource_id,
        action=req.action,
        is_emergency=req.is_emergency,
        tenant_id=req.tenant_id,
    )
    return rem.model_dump()


@router.post("/remediation/{remediation_id}/execute", status_code=status.HTTP_200_OK)
def execute_remediation(
    remediation_id: str,
    mgr: GovernancePlatformManager = Depends(get_governance_manager),
):
    try:
        rem = mgr.enforcement_engine.execute_remediation(remediation_id)
        return rem.model_dump()
    except KeyError:
        raise HTTPException(status_code=404, detail="Remediation not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/reports/audit-package", status_code=status.HTTP_200_OK)
def get_audit_package(
    tenant_id: str = Query("global"),
    scope: str = Query("TENANT"),
    mgr: GovernancePlatformManager = Depends(get_governance_manager),
):
    pkg = mgr.report_generator.generate_audit_package(tenant_id=tenant_id, scope=scope)
    return pkg.model_dump()
