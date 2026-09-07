"""FastAPI REST API Router for Phase 5.52 Enterprise AI Decision Intelligence Platform."""

import logging
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Header, status

from app.decision_intelligence.manager import DecisionIntelligenceManager
from app.decision_intelligence.schemas import (
    DecisionCreateRequest,
    DecisionOptionCreateRequest,
    DecisionStateTransitionRequest,
    DecisionApprovalRequest,
    DecisionSimulationRequest,
    DecisionResponse,
    DecisionOptionResponse,
    DecisionRecommendationResponse,
    DecisionSimulationResultResponse,
    DecisionReproducibilityRecordResponse,
)
from app.decision_intelligence.exceptions import (
    DecisionIntelligenceException,
    DecisionNotFoundException,
    InvalidDecisionStateTransitionException,
    CrossTenantDecisionIntelligenceException,
    HighRiskDecisionRequiresApprovalException,
)
from app.decision_intelligence.decisions import DecisionLifecycleState, DecisionType

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1/decisions", tags=["Decision Intelligence"])

# Shared manager instance for API requests
_decision_manager = DecisionIntelligenceManager()


def get_tenant_id(x_tenant_id: Optional[str] = Header("default", alias="X-Tenant-ID")) -> str:
    return x_tenant_id or "default"


@router.post("", response_model=DecisionResponse, status_code=status.HTTP_201_CREATED)
def create_decision(request: DecisionCreateRequest, tenant_id: str = Depends(get_tenant_id)) -> DecisionResponse:
    """Create a new enterprise decision request in PROPOSED state."""
    try:
        dtype = DecisionType(request.decision_type) if request.decision_type in DecisionType.__members__ else DecisionType.CROSS_DOMAIN
        dec = _decision_manager.decision_manager.create_decision(
            tenant_id=tenant_id,
            title=request.title,
            decision_type=dtype,
            description=request.description,
        )
        return DecisionResponse(
            id=dec.decision_id,
            tenant_id=dec.tenant_id,
            title=dec.title,
            description=dec.description,
            state=dec.state.value,
            decision_type=dec.decision_type.value,
            scope=request.scope,
            risk_level=dec.risk_level,
            confidence_score=dec.confidence_score,
            uncertainty_score=dec.uncertainty_score,
            created_at=dec.created_at.isoformat(),
            updated_at=dec.updated_at.isoformat(),
            fingerprint=dec.decision_fingerprint,
            metadata=dec.metadata,
        )
    except Exception as e:
        logger.error(f"Failed to create decision: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{decision_id}", response_model=DecisionResponse)
def get_decision(decision_id: str, tenant_id: str = Depends(get_tenant_id)) -> DecisionResponse:
    """Retrieve decision by ID with strict tenant isolation."""
    try:
        dec = _decision_manager.decision_manager.get_decision(decision_id, tenant_id)
        return DecisionResponse(
            id=dec.decision_id,
            tenant_id=dec.tenant_id,
            title=dec.title,
            description=dec.description,
            state=dec.state.value,
            decision_type=dec.decision_type.value,
            scope="ENTERPRISE",
            risk_level=dec.risk_level,
            confidence_score=dec.confidence_score,
            uncertainty_score=dec.uncertainty_score,
            created_at=dec.created_at.isoformat(),
            updated_at=dec.updated_at.isoformat(),
            fingerprint=dec.decision_fingerprint,
            metadata=dec.metadata,
        )
    except CrossTenantDecisionIntelligenceException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except DecisionNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/{decision_id}/transition", response_model=DecisionResponse)
def transition_decision_state(
    decision_id: str,
    request: DecisionStateTransitionRequest,
    tenant_id: str = Depends(get_tenant_id),
) -> DecisionResponse:
    """Transition decision lifecycle state with strict state machine validation."""
    try:
        target = DecisionLifecycleState(request.target_state)
        dec = _decision_manager.decision_manager.update_decision_state(decision_id, tenant_id, target, reason=request.reason)
        return DecisionResponse(
            id=dec.decision_id,
            tenant_id=dec.tenant_id,
            title=dec.title,
            description=dec.description,
            state=dec.state.value,
            decision_type=dec.decision_type.value,
            scope="ENTERPRISE",
            risk_level=dec.risk_level,
            confidence_score=dec.confidence_score,
            uncertainty_score=dec.uncertainty_score,
            created_at=dec.created_at.isoformat(),
            updated_at=dec.updated_at.isoformat(),
            fingerprint=dec.decision_fingerprint,
            metadata=dec.metadata,
        )
    except InvalidDecisionStateTransitionException as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except CrossTenantDecisionIntelligenceException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except DecisionNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/{decision_id}/options", response_model=DecisionOptionResponse, status_code=status.HTTP_201_CREATED)
def add_decision_option(
    decision_id: str,
    request: DecisionOptionCreateRequest,
    tenant_id: str = Depends(get_tenant_id),
) -> DecisionOptionResponse:
    """Add a candidate decision option."""
    try:
        opt = _decision_manager.options_registry.add_option(
            decision_id=decision_id,
            tenant_id=tenant_id,
            title=request.title,
            description=request.description,
            action_type=request.action_type,
            target_system=request.target_system,
            parameters=request.parameters,
            estimated_cost=request.estimated_cost,
            reversibility=request.reversibility,
        )
        return DecisionOptionResponse(
            id=opt.option_id,
            decision_id=opt.decision_id,
            tenant_id=opt.tenant_id,
            title=opt.title,
            description=opt.description,
            action_type=opt.action_type,
            target_system=opt.target_system,
            parameters=opt.parameters,
            score=opt.score,
            estimated_cost=opt.estimated_cost,
            reversibility=opt.reversibility,
        )
    except CrossTenantDecisionIntelligenceException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.post("/{decision_id}/simulate", response_model=DecisionSimulationResultResponse)
def simulate_decision(
    decision_id: str,
    request: DecisionSimulationRequest,
    tenant_id: str = Depends(get_tenant_id),
) -> DecisionSimulationResultResponse:
    """Run what-if simulation across candidate decision options."""
    try:
        options = request.options
        if not options:
            opts = _decision_manager.options_registry.list_options(decision_id, tenant_id)
            options = [o.model_dump() for o in opts]

        res = _decision_manager.simulation_engine.simulate_decision_options(
            decision_id=decision_id,
            tenant_id=tenant_id,
            options=options,
            scenarios=request.scenarios,
        )
        return DecisionSimulationResultResponse(
            simulation_id=res.simulation_id,
            decision_id=res.decision_id,
            tenant_id=res.tenant_id,
            compared_options=[o.model_dump() for o in res.compared_options],
            best_option_id=res.recommended_option_id,
            tradeoffs=res.tradeoffs,
            simulated_impact=res.impact_simulation,
            simulated_risk=res.risk_simulation,
        )
    except CrossTenantDecisionIntelligenceException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{decision_id}/reproducibility", response_model=DecisionReproducibilityRecordResponse)
def get_reproducibility_record(decision_id: str, tenant_id: str = Depends(get_tenant_id)) -> DecisionReproducibilityRecordResponse:
    """Get decision reproducibility record and verify integrity."""
    try:
        rec = _decision_manager.reproducibility_engine.get_reproducibility_record(decision_id, tenant_id)
        _decision_manager.reproducibility_engine.verify_reproducibility(decision_id, tenant_id)
        return DecisionReproducibilityRecordResponse(
            id=rec.record_id,
            decision_id=rec.decision_id,
            tenant_id=rec.tenant_id,
            context_fingerprint=rec.context_fingerprint,
            evidence_hashes=rec.evidence_hashes,
            model_version=rec.model_version,
            scoring_config_version=rec.scoring_config_version,
            policy_evaluation_id=str(rec.policy_evaluation_result.get("evaluation_id", "pol_001")),
            risk_assessment_id=f"risk_v_{rec.risk_assessment_version}",
            timestamp=rec.created_at.isoformat(),
        )
    except CrossTenantDecisionIntelligenceException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except DecisionNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/{decision_id}/approve", status_code=status.HTTP_200_OK)
def approve_decision(decision_id: str, request: DecisionApprovalRequest, tenant_id: str = Depends(get_tenant_id)) -> Dict[str, Any]:
    """Submit human approval for a decision requiring review."""
    try:
        rec = _decision_manager.approval_manager.submit_approval(
            decision_id=decision_id,
            tenant_id=tenant_id,
            approver=request.approver,
            approved=request.approved,
            comments=request.comments,
        )
        if request.approved:
            dec = _decision_manager.decision_manager.get_decision(decision_id, tenant_id)
            if dec.state == DecisionLifecycleState.REQUIRES_APPROVAL:
                dec.transition_to(DecisionLifecycleState.APPROVED, reason=f"Approved by {request.approver}")
        return {"status": "SUCCESS", "approval": rec.model_dump()}
    except CrossTenantDecisionIntelligenceException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.post("/flow", status_code=status.HTTP_200_OK)
def run_full_flow(title: str = "Enterprise Architecture Modernization", tenant_id: str = Depends(get_tenant_id)) -> Dict[str, Any]:
    """Run full end-to-end decision intelligence lifecycle flow."""
    try:
        return _decision_manager.run_full_decision_flow(tenant_id=tenant_id, title=title)
    except Exception as e:
        logger.error(f"Decision flow failed: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
