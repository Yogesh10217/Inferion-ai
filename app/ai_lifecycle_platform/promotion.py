"""Controlled Promotion Workflow Subsystem (Phase 5.33)."""

from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.approvals.approval_engine import ApprovalEngine
from app.ai_lifecycle_platform.exceptions import InvalidPromotionException, HighRiskReleaseRequiresApprovalException, EvaluationGateFailedException
from app.ai_lifecycle_platform.gates import GateStatus, GateEvaluation


class PromotionTarget(str, Enum):
    DEVELOPMENT = "DEVELOPMENT"
    TEST = "TEST"
    STAGING = "STAGING"
    PRODUCTION = "PRODUCTION"


class PromotionStatus(str, Enum):
    PROPOSED = "PROPOSED"
    EVALUATING = "EVALUATING"
    REQUIRE_APPROVAL = "REQUIRE_APPROVAL"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    PROMOTED = "PROMOTED"


class PromotionDecision(BaseModel):
    decision_id: str = Field(default_factory=lambda: f"promdec_{uuid.uuid4().hex[:12]}")
    status: PromotionStatus = PromotionStatus.APPROVED
    reason: str = "All promotion gates passed"


class PromotionRequest(BaseModel):
    request_id: str = Field(default_factory=lambda: f"promreq_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    asset_id: str
    target: PromotionTarget = PromotionTarget.STAGING
    is_high_risk: bool = False
    evaluations_passed: bool = True
    gate_evaluations: List[GateEvaluation] = Field(default_factory=list)
    status: PromotionStatus = PromotionStatus.PROPOSED
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class PromotionManager:
    """Manages controlled AI asset promotion across environments."""

    def __init__(self, approval_engine: Optional[ApprovalEngine] = None) -> None:
        self.approval_engine = approval_engine or ApprovalEngine()
        self._requests: Dict[str, PromotionRequest] = {}

    def request_promotion(
        self,
        tenant_id: str,
        asset_id: str,
        target: PromotionTarget = PromotionTarget.STAGING,
        evaluations_passed: bool = True,
        gate_evaluations: Optional[List[GateEvaluation]] = None,
        is_high_risk: bool = False,
    ) -> PromotionRequest:
        gates = gate_evaluations or []

        # Check for hard gate failures
        for g in gates:
            if g.status == GateStatus.FAILED:
                raise EvaluationGateFailedException(g.gate_type.value, g.message)

        if not evaluations_passed:
            raise InvalidPromotionException("Evaluations did not pass.")

        req = PromotionRequest(
            tenant_id=tenant_id,
            asset_id=asset_id,
            target=target,
            evaluations_passed=evaluations_passed,
            gate_evaluations=gates,
            is_high_risk=is_high_risk,
        )

        if target == PromotionTarget.PRODUCTION and is_high_risk:
            req.status = PromotionStatus.REQUIRE_APPROVAL
            self.approval_engine.request_approval(
                execution_id=req.request_id,
                action_type="HIGH_RISK_AI_PROMOTION",
                tenant_id=tenant_id,
                requester="ai_lifecycle_platform",
            )
        else:
            req.status = PromotionStatus.APPROVED

        self._requests[req.request_id] = req
        return req
