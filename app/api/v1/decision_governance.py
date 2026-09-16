"""FastAPI REST API endpoints for Phase 5.45 Decision Governance platform."""

from typing import Any, Dict, List

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel

from app.decision_governance.decisions import DecisionPriority, DecisionType
from app.decision_governance.exceptions import (
    CrossTenantDecisionGovernanceException,
    DecisionNotFoundException,
    HighRiskDecisionRequiresApprovalException,
)
from app.decision_governance.manager import DecisionGovernanceManager

router = APIRouter(prefix="/v1/decisions", tags=["Decision Governance"])

# Singleton manager instance
_manager = DecisionGovernanceManager()


def get_manager() -> DecisionGovernanceManager:
    return _manager


class CreateDecisionRequest(BaseModel):
    title: str
    decision_type: DecisionType = DecisionType.OPERATIONAL
    description: str = ""
    priority: DecisionPriority = DecisionPriority.MEDIUM
    metadata: Dict[str, Any] = {}


class DelegateDecisionRequest(BaseModel):
    actions: List[Dict[str, Any]]


@router.post("", response_model=Dict[str, Any])
def create_decision(
    req: CreateDecisionRequest,
    x_tenant_id: str = Header(default="default_tenant"),
    mgr: DecisionGovernanceManager = Depends(get_manager),
):
    try:
        decision = mgr.create_decision(
            tenant_id=x_tenant_id,
            title=req.title,
            decision_type=req.decision_type,
            description=req.description,
            priority=req.priority,
            metadata=req.metadata,
        )
        return decision.model_dump()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=List[Dict[str, Any]])
def list_decisions(
    x_tenant_id: str = Header(default="default_tenant"),
    mgr: DecisionGovernanceManager = Depends(get_manager),
):
    decisions = mgr.list_decisions(tenant_id=x_tenant_id)
    return [d.model_dump() for d in decisions]


@router.get("/{decision_id}", response_model=Dict[str, Any])
def get_decision(
    decision_id: str,
    x_tenant_id: str = Header(default="default_tenant"),
    mgr: DecisionGovernanceManager = Depends(get_manager),
):
    try:
        decision = mgr.get_decision(decision_id, tenant_id=x_tenant_id)
        return decision.model_dump()
    except CrossTenantDecisionGovernanceException:
        raise HTTPException(status_code=403, detail="Access denied")
    except DecisionNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{decision_id}/analyze", response_model=Dict[str, Any])
def analyze_decision(
    decision_id: str,
    x_tenant_id: str = Header(default="default_tenant"),
    mgr: DecisionGovernanceManager = Depends(get_manager),
):
    try:
        res = mgr.analyze_and_governed_evaluate(decision_id, tenant_id=x_tenant_id)
        return res.model_dump()
    except CrossTenantDecisionGovernanceException:
        raise HTTPException(status_code=403, detail="Access denied")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{decision_id}/approve", response_model=Dict[str, Any])
def approve_decision(
    decision_id: str,
    x_tenant_id: str = Header(default="default_tenant"),
    mgr: DecisionGovernanceManager = Depends(get_manager),
):
    try:
        decision = mgr.approve_decision(decision_id, tenant_id=x_tenant_id)
        return decision.model_dump()
    except CrossTenantDecisionGovernanceException:
        raise HTTPException(status_code=403, detail="Access denied")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{decision_id}/delegate", response_model=Dict[str, Any])
def delegate_decision(
    decision_id: str,
    req: DelegateDecisionRequest,
    x_tenant_id: str = Header(default="default_tenant"),
    mgr: DecisionGovernanceManager = Depends(get_manager),
):
    try:
        from app.decision_governance.delegation import DecisionDelegationAction

        actions = [
            DecisionDelegationAction(
                target_type=a.get("target_type", "SERVICE"),
                target_id=a.get("target_id", "srv-1"),
                action_name=a.get("action_name", "EXECUTE"),
                parameters=a.get("parameters", {}),
            )
            for a in req.actions
        ]
        plan = mgr.delegate_decision(decision_id, tenant_id=x_tenant_id, actions=actions)
        return plan.model_dump()
    except HighRiskDecisionRequiresApprovalException as e:
        raise HTTPException(status_code=402, detail=str(e))
    except CrossTenantDecisionGovernanceException:
        raise HTTPException(status_code=403, detail="Access denied")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{decision_id}/verify", response_model=Dict[str, Any])
def verify_decision(
    decision_id: str,
    x_tenant_id: str = Header(default="default_tenant"),
    mgr: DecisionGovernanceManager = Depends(get_manager),
):
    try:
        finalized = mgr.verify_and_finalize(decision_id, tenant_id=x_tenant_id)
        return finalized.model_dump()
    except CrossTenantDecisionGovernanceException:
        raise HTTPException(status_code=403, detail="Access denied")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{decision_id}/explain", response_model=Dict[str, Any])
def explain_decision(
    decision_id: str,
    x_tenant_id: str = Header(default="default_tenant"),
    mgr: DecisionGovernanceManager = Depends(get_manager),
):
    try:
        exp = mgr.explainability.generate_explanation(
            tenant_id=x_tenant_id,
            decision_id=decision_id,
            why_summary="Decision optimized based on multi-domain confidence and low risk score",
            expected_outcome="Positive operational gain and zero SLA breach",
        )
        return exp.model_dump()
    except CrossTenantDecisionGovernanceException:
        raise HTTPException(status_code=403, detail="Access denied")


@router.get("/analytics/reports", response_model=Dict[str, Any])
def get_analytics_report(
    x_tenant_id: str = Header(default="default_tenant"),
    mgr: DecisionGovernanceManager = Depends(get_manager),
):
    decisions = mgr.list_decisions(tenant_id=x_tenant_id)
    report = mgr.analytics.generate_analytics_report(tenant_id=x_tenant_id, decisions=decisions)
    return report.model_dump()
