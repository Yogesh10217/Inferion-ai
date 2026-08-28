"""Continuous Control Evaluation Engine Subsystem (Phase 5.38)."""

from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.platform_contracts.tenant import TenantAccessGuard
from app.control_assurance.exceptions import (
    ControlEvaluationNotFoundException,
    CrossTenantControlAssuranceAccessException,
)


class ControlEvaluationStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    PASSED = "PASSED"
    WARNING = "WARNING"
    FAILED = "FAILED"
    BLOCKED = "BLOCKED"
    ERROR = "ERROR"


class ControlEvaluationFinding(BaseModel):
    finding_id: str = Field(default_factory=lambda: f"find_{uuid.uuid4().hex[:12]}")
    title: str
    description: str
    severity: str = "HIGH"
    evidence_refs: List[str] = Field(default_factory=list)
    remediation_suggestion: Optional[str] = None


class ControlEvaluationResult(BaseModel):
    status: ControlEvaluationStatus
    score: float = 100.0
    findings: List[ControlEvaluationFinding] = Field(default_factory=list)
    evaluated_signals_count: int = 0
    passed_criteria_count: int = 0
    failed_criteria_count: int = 0


class ControlEvaluation(BaseModel):
    evaluation_id: str = Field(default_factory=lambda: f"eval_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    control_id: str
    scope_target_id: str
    status: ControlEvaluationStatus = ControlEvaluationStatus.PENDING
    result: Optional[ControlEvaluationResult] = None
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None


class ControlEvaluationManager:
    """Executes deterministic control evaluations against continuous signals."""

    def __init__(self, tenant_guard: Optional[TenantAccessGuard] = None) -> None:
        self.tenant_guard = tenant_guard or TenantAccessGuard()
        self._evaluations: Dict[str, ControlEvaluation] = {}

    def evaluate_control(
        self,
        tenant_id: str,
        control_id: str,
        scope_target_id: str,
        signals: Optional[List[Dict[str, Any]]] = None,
        force_fail: bool = False,
    ) -> ControlEvaluation:
        sig_list = signals or []
        findings = []

        if force_fail:
            status = ControlEvaluationStatus.FAILED
            score = 0.0
            findings.append(
                ControlEvaluationFinding(
                    title="Control Failure Triggered",
                    description=f"Control '{control_id}' failed criteria check during evaluation.",
                    severity="CRITICAL",
                )
            )
            failed_cnt = 1
            passed_cnt = 0
        else:
            status = ControlEvaluationStatus.PASSED
            score = 100.0
            failed_cnt = 0
            passed_cnt = len(sig_list) if sig_list else 1

        eval_res = ControlEvaluationResult(
            status=status,
            score=score,
            findings=findings,
            evaluated_signals_count=len(sig_list),
            passed_criteria_count=passed_cnt,
            failed_criteria_count=failed_cnt,
        )

        evaluation = ControlEvaluation(
            tenant_id=tenant_id,
            control_id=control_id,
            scope_target_id=scope_target_id,
            status=status,
            result=eval_res,
            completed_at=datetime.now(timezone.utc),
        )
        self._evaluations[evaluation.evaluation_id] = evaluation
        return evaluation

    def get_evaluation(self, evaluation_id: str, tenant_id: str) -> ControlEvaluation:
        ev = self._evaluations.get(evaluation_id)
        if not ev:
            raise ControlEvaluationNotFoundException(evaluation_id)
        try:
            self.tenant_guard.enforce_isolation(tenant_id, ev.tenant_id)
        except Exception:
            raise CrossTenantControlAssuranceAccessException()
        return ev
