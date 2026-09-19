"""Explainability Intelligence (Phase 5.44)."""

import hashlib
import logging
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class ExplanationType(str, Enum):
    DECISION_REASONING_REF = "DECISION_REASONING_REF"
    EVIDENCE_REF = "EVIDENCE_REF"
    EVALUATION_EXPLANATION = "EVALUATION_EXPLANATION"
    CONFIDENCE_ANALYSIS = "CONFIDENCE_ANALYSIS"
    MODEL_BEHAVIOR_EXPLANATION = "MODEL_BEHAVIOR_EXPLANATION"


class ExplanationEvidence(BaseModel):
    evidence_id: str
    summary_hash: str
    feature_attributions: Dict[str, float] = Field(default_factory=dict)
    sanitized_reasoning: str = "[REDACTED_INTERNAL_REASONING]"


class ModelExplanation(BaseModel):
    explanation_id: str
    model_id: str
    tenant_id: str
    explanation_type: ExplanationType
    confidence_score: float  # 0.0 - 1.0
    summary: str
    evidence: ExplanationEvidence
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ExplainabilityAssessment(BaseModel):
    assessment_id: str
    model_id: str
    tenant_id: str
    overall_explainability_score: float  # 0.0 - 1.0
    explanations: List[ModelExplanation] = Field(default_factory=list)
    assessed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ModelExplainabilityManager:
    """Manages explainability intelligence without exposing hidden internal chain-of-thought."""

    def __init__(self) -> None:
        self._explanations: Dict[str, ModelExplanation] = {}

    def generate_explanation(
        self,
        model_id: str,
        tenant_id: str,
        explanation_type: ExplanationType,
        summary: str,
        confidence_score: float = 0.95,
        feature_attributions: Optional[Dict[str, float]] = None,
    ) -> ModelExplanation:
        e_id = f"exp-{uuid.uuid4().hex[:8]}"
        atts = feature_attributions or {}
        fp = hashlib.sha256(f"{model_id}:{summary}:{confidence_score}".encode()).hexdigest()

        evidence = ExplanationEvidence(
            evidence_id=f"exevid-{uuid.uuid4().hex[:6]}",
            summary_hash=fp,
            feature_attributions=atts,
            sanitized_reasoning="Sanitized high-level reasoning reference only.",
        )

        explanation = ModelExplanation(
            explanation_id=e_id,
            model_id=model_id,
            tenant_id=tenant_id,
            explanation_type=explanation_type,
            confidence_score=confidence_score,
            summary=summary,
            evidence=evidence,
        )

        self._explanations[e_id] = explanation
        logger.info(
            f"[MODEL EXPLAINABILITY] Generated explanation for {model_id} (Tenant: {tenant_id}) Type: {explanation_type}"
        )
        return explanation

    def get_explainability_assessment(self, model_id: str, tenant_id: str) -> ExplainabilityAssessment:
        exps = [e for e in self._explanations.values() if e.model_id == model_id and e.tenant_id == tenant_id]
        overall = sum(e.confidence_score for e in exps) / max(len(exps), 1) if exps else 1.0

        return ExplainabilityAssessment(
            assessment_id=f"expassess-{uuid.uuid4().hex[:8]}",
            model_id=model_id,
            tenant_id=tenant_id,
            overall_explainability_score=overall,
            explanations=exps,
        )
