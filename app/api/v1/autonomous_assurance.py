"""FastAPI REST API Router for Phase 5.53 Enterprise AI Autonomous Assurance Platform."""

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, Header, HTTPException, status

from app.autonomous_assurance.exceptions import (
    AutonomousWorkflowNotFoundException,
    CrossTenantAutonomousAssuranceException,
    HighRiskAutonomousActionRequiresApprovalException,
)
from app.autonomous_assurance.manager import AutonomousAssuranceManager
from app.autonomous_assurance.schemas import (
    AssuranceResponse,
    DelegationResponse,
    PlanCreateRequest,
    PlanResponse,
    RecoveryResponse,
    VerificationResponse,
    WorkflowApprovalRequest,
    WorkflowCreateRequest,
    WorkflowResponse,
)
from app.autonomous_assurance.workflows import WorkflowPriority, WorkflowType

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1/autonomous", tags=["Autonomous Assurance"])

_manager = AutonomousAssuranceManager()


def get_tenant_id(x_tenant_id: Optional[str] = Header("default", alias="X-Tenant-ID")) -> str:
    return x_tenant_id or "default"


@router.post("/workflows", response_model=WorkflowResponse, status_code=status.HTTP_201_CREATED)
def create_workflow(request: WorkflowCreateRequest, tenant_id: str = Depends(get_tenant_id)) -> WorkflowResponse:
    """Create a new autonomous workflow."""
    try:
        wtype = (
            WorkflowType(request.workflow_type)
            if request.workflow_type in WorkflowType.__members__
            else WorkflowType.CROSS_DOMAIN_COORDINATION
        )
        wpri = (
            WorkflowPriority(request.priority)
            if request.priority in WorkflowPriority.__members__
            else WorkflowPriority.MEDIUM
        )
        wf = _manager.create_workflow(
            tenant_id=tenant_id,
            title=request.title,
            workflow_type=wtype,
            description=request.description,
            priority=wpri,
        )
        return WorkflowResponse(
            workflow_id=wf.workflow_id,
            tenant_id=wf.tenant_id,
            title=wf.title,
            description=wf.description,
            workflow_type=wf.workflow_type.value,
            status=wf.status.value,
            priority=wf.priority.value,
            plan_id=wf.plan_id,
            delegation_id=wf.delegation_id,
            verification_id=wf.verification_id,
            evidence_id=wf.evidence_id,
            is_finalized=wf.is_finalized,
            created_at=wf.created_at.isoformat(),
            updated_at=wf.updated_at.isoformat(),
        )
    except Exception as e:
        logger.error(f"Failed to create workflow: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/workflows/{workflow_id}", response_model=WorkflowResponse)
def get_workflow(workflow_id: str, tenant_id: str = Depends(get_tenant_id)) -> WorkflowResponse:
    """Retrieve workflow by ID with strict tenant isolation."""
    try:
        wf = _manager.get_workflow(workflow_id, tenant_id)
        return WorkflowResponse(
            workflow_id=wf.workflow_id,
            tenant_id=wf.tenant_id,
            title=wf.title,
            description=wf.description,
            workflow_type=wf.workflow_type.value,
            status=wf.status.value,
            priority=wf.priority.value,
            plan_id=wf.plan_id,
            delegation_id=wf.delegation_id,
            verification_id=wf.verification_id,
            evidence_id=wf.evidence_id,
            is_finalized=wf.is_finalized,
            created_at=wf.created_at.isoformat(),
            updated_at=wf.updated_at.isoformat(),
        )
    except CrossTenantAutonomousAssuranceException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except AutonomousWorkflowNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/workflows", response_model=List[WorkflowResponse])
def list_workflows(tenant_id: str = Depends(get_tenant_id)) -> List[WorkflowResponse]:
    """List all autonomous workflows for a tenant."""
    wfs = _manager.workflow_repo.list_by_tenant(tenant_id)
    return [
        WorkflowResponse(
            workflow_id=wf.workflow_id,
            tenant_id=wf.tenant_id,
            title=wf.title,
            description=wf.description,
            workflow_type=wf.workflow_type.value,
            status=wf.status.value,
            priority=wf.priority.value,
            plan_id=wf.plan_id,
            delegation_id=wf.delegation_id,
            verification_id=wf.verification_id,
            evidence_id=wf.evidence_id,
            is_finalized=wf.is_finalized,
            created_at=wf.created_at.isoformat(),
            updated_at=wf.updated_at.isoformat(),
        )
        for wf in wfs
    ]


@router.post("/workflows/{workflow_id}/plan", response_model=PlanResponse)
def create_plan(workflow_id: str, request: PlanCreateRequest, tenant_id: str = Depends(get_tenant_id)) -> PlanResponse:
    """Generate workflow plan."""
    try:
        plan = _manager.create_plan(
            workflow_id, tenant_id, risk_score=request.risk_score, trust_score=request.trust_score
        )
        return PlanResponse(
            plan_id=plan.plan_id,
            workflow_id=plan.workflow_id,
            tenant_id=plan.tenant_id,
            plan_steps=[s.model_dump() for s in plan.plan_steps],
            risk_score=plan.risk_score,
            trust_score=plan.trust_score,
            requires_approval=plan.requires_approval,
            created_at=plan.created_at.isoformat(),
        )
    except AutonomousWorkflowNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/workflows/{workflow_id}/governance")
def evaluate_governance(
    workflow_id: str, risk_score: float = 20.0, trust_score: float = 90.0, tenant_id: str = Depends(get_tenant_id)
) -> Dict[str, Any]:
    """Evaluate workflow governance policies."""
    try:
        gov = _manager.evaluate_governance(workflow_id, tenant_id, risk_score=risk_score, trust_score=trust_score)
        return gov.model_dump()
    except AutonomousWorkflowNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/workflows/{workflow_id}/approve", response_model=WorkflowResponse)
def approve_workflow(
    workflow_id: str, request: WorkflowApprovalRequest, tenant_id: str = Depends(get_tenant_id)
) -> WorkflowResponse:
    """Approve a workflow requiring review."""
    try:
        wf = _manager.approve_workflow(
            workflow_id, tenant_id, approver=request.approved_by, approved=True, comments=request.comments
        )
        return get_workflow(wf.workflow_id, tenant_id)
    except AutonomousWorkflowNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/workflows/{workflow_id}/reject", response_model=WorkflowResponse)
def reject_workflow(
    workflow_id: str, request: WorkflowApprovalRequest, tenant_id: str = Depends(get_tenant_id)
) -> WorkflowResponse:
    """Reject a workflow."""
    try:
        wf = _manager.approve_workflow(
            workflow_id, tenant_id, approver=request.approved_by, approved=False, comments=request.comments
        )
        return get_workflow(wf.workflow_id, tenant_id)
    except AutonomousWorkflowNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/workflows/{workflow_id}/delegate", response_model=DelegationResponse)
def delegate_workflow(
    workflow_id: str, action_name: str = "RESTART_SERVICE", tenant_id: str = Depends(get_tenant_id)
) -> DelegationResponse:
    """Dispatch formal DelegationRequest (Zero direct execution)."""
    try:
        del_plan = _manager.delegate_workflow(workflow_id, tenant_id, action_name=action_name)
        return DelegationResponse(
            delegation_id=del_plan.delegation_id,
            workflow_id=del_plan.workflow_id,
            tenant_id=del_plan.tenant_id,
            target_subsystem=del_plan.target_subsystem,
            action_type=del_plan.action_type,
            delegation_request=del_plan.delegation_request.model_dump(),
            created_at=del_plan.created_at.isoformat(),
        )
    except HighRiskAutonomousActionRequiresApprovalException as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except AutonomousWorkflowNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/workflows/{workflow_id}/verify", response_model=VerificationResponse)
def verify_workflow(
    workflow_id: str, simulate_failure: bool = False, tenant_id: str = Depends(get_tenant_id)
) -> VerificationResponse:
    """Verify outcome post-delegation."""
    try:
        res = _manager.verify_workflow(workflow_id, tenant_id, simulate_failure=simulate_failure)
        return VerificationResponse(
            verification_id=res.verification_id,
            workflow_id=res.workflow_id,
            tenant_id=res.tenant_id,
            delegation_id=res.delegation_id,
            status=res.status.value,
            passed_checks=res.passed_checks,
            metrics_summary=res.metrics_summary,
            verified_at=res.verified_at.isoformat(),
        )
    except AutonomousWorkflowNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/workflows/{workflow_id}/recover", response_model=RecoveryResponse)
def recover_workflow(
    workflow_id: str, failure_reason: str = "Verification failed", tenant_id: str = Depends(get_tenant_id)
) -> RecoveryResponse:
    """Plan recovery for a failed workflow step."""
    try:
        plan = _manager.recover_workflow(workflow_id, tenant_id, failure_reason=failure_reason)
        return RecoveryResponse(
            recovery_id=plan.recovery_id,
            workflow_id=plan.workflow_id,
            tenant_id=plan.tenant_id,
            failure_reason=plan.failure_reason,
            recovery_steps=[s.model_dump() for s in plan.recovery_steps],
            created_at=plan.created_at.isoformat(),
        )
    except AutonomousWorkflowNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/workflows/{workflow_id}/evidence")
def get_evidence(workflow_id: str, tenant_id: str = Depends(get_tenant_id)) -> Dict[str, Any]:
    """Retrieve immutable evidence bundle."""
    try:
        bundle = _manager.evidence_manager.get_evidence_bundle(workflow_id, tenant_id)
        return bundle.model_dump()
    except CrossTenantAutonomousAssuranceException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.get("/workflows/{workflow_id}/assurance", response_model=AssuranceResponse)
def get_assurance(workflow_id: str, tenant_id: str = Depends(get_tenant_id)) -> AssuranceResponse:
    """Retrieve assurance score."""
    try:
        score = _manager.assurance_engine.get_assurance(workflow_id) or _manager.assurance_engine.calculate_assurance(
            workflow_id, tenant_id
        )
        return AssuranceResponse(
            score_id=score.score_id,
            workflow_id=score.workflow_id,
            tenant_id=score.tenant_id,
            overall_assurance_score=score.overall_assurance_score,
            assurance_rating=score.assurance_rating,
            evaluated_at=score.evaluated_at.isoformat(),
        )
    except AutonomousWorkflowNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/flow")
def run_flow(
    title: str = "Enterprise Autonomous Assurance Flow", tenant_id: str = Depends(get_tenant_id)
) -> Dict[str, Any]:
    """Run full end-to-end autonomous assurance workflow lifecycle."""
    try:
        return _manager.run_full_autonomous_flow(tenant_id=tenant_id, title=title)
    except Exception as e:
        logger.error(f"Autonomous flow failed: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
