"""Deterministic & Governed Model Evaluation (Phase 5.44)."""

import hashlib
import logging
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.model_intelligence.exceptions import CrossTenantModelIntelligenceException, ModelEvaluationNotFoundException

logger = logging.getLogger(__name__)


class EvaluationType(str, Enum):
    DETERMINISTIC = "DETERMINISTIC"
    HUMAN_EVAL = "HUMAN_EVAL"
    AUTOMATED_LLM_JUDGE = "AUTOMATED_LLM_JUDGE"
    BENCHMARK = "BENCHMARK"


class EvaluationStatus(str, Enum):
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class EvaluationMetric(BaseModel):
    name: str
    score: float
    min_threshold: Optional[float] = None
    passed: bool = True
    details: Dict[str, Any] = Field(default_factory=dict)


class EvaluationEvidence(BaseModel):
    evidence_id: str
    dataset_name: str
    sample_count: int
    fingerprint: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class EvaluationResult(BaseModel):
    overall_score: float
    metrics: List[EvaluationMetric]
    status: EvaluationStatus = EvaluationStatus.COMPLETED
    passed: bool = True


class ModelEvaluation(BaseModel):
    evaluation_id: str
    model_id: str
    tenant_id: str
    version_tag: str
    eval_type: EvaluationType
    result: EvaluationResult
    evidence: EvaluationEvidence
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ModelEvaluationManager:
    """Manages deterministic and governed model evaluations."""

    def __init__(self) -> None:
        self._evaluations: Dict[str, ModelEvaluation] = {}

    def create_evaluation(
        self,
        model_id: str,
        tenant_id: str,
        version_tag: str,
        eval_type: EvaluationType,
        metrics: List[EvaluationMetric],
        dataset_name: str = "default_eval_dataset",
        sample_count: int = 100,
    ) -> ModelEvaluation:
        eval_id = f"eval-{uuid.uuid4().hex[:8]}"
        overall = sum(m.score for m in metrics) / max(len(metrics), 1)
        passed = all(m.passed for m in metrics)

        result = EvaluationResult(overall_score=overall, metrics=metrics, passed=passed)

        evidence_payload = f"{model_id}:{tenant_id}:{version_tag}:{dataset_name}:{sample_count}"
        fp = hashlib.sha256(evidence_payload.encode()).hexdigest()

        evidence = EvaluationEvidence(
            evidence_id=f"evid-{uuid.uuid4().hex[:6]}",
            dataset_name=dataset_name,
            sample_count=sample_count,
            fingerprint=fp,
        )

        evaluation = ModelEvaluation(
            evaluation_id=eval_id,
            model_id=model_id,
            tenant_id=tenant_id,
            version_tag=version_tag,
            eval_type=eval_type,
            result=result,
            evidence=evidence,
        )

        self._evaluations[eval_id] = evaluation
        logger.info(f"[MODEL EVALUATION] Evaluated model {model_id} (Tenant: {tenant_id}) Score: {overall:.2f}")
        return evaluation

    def get_evaluation(self, evaluation_id: str, tenant_id: str) -> ModelEvaluation:
        ev = self._evaluations.get(evaluation_id)
        if not ev:
            raise ModelEvaluationNotFoundException(f"Evaluation '{evaluation_id}' not found.")
        if ev.tenant_id != tenant_id:
            raise CrossTenantModelIntelligenceException()
        return ev

    def list_evaluations(self, tenant_id: str, model_id: Optional[str] = None) -> List[ModelEvaluation]:
        res = [e for e in self._evaluations.values() if e.tenant_id == tenant_id]
        if model_id:
            res = [e for e in res if e.model_id == model_id]
        return res
