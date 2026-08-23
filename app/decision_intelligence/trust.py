"""Enterprise Decision Trust Engine Subsystem."""

from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field


class DecisionTrustDimension(str, Enum):
    EVIDENCE_QUALITY = "EVIDENCE_QUALITY"
    DATA_TRUST = "DATA_TRUST"
    ARCHITECTURE_TRUST = "ARCHITECTURE_TRUST"
    COMPLIANCE_TRUST = "COMPLIANCE_TRUST"
    PORTFOLIO_TRUST = "PORTFOLIO_TRUST"
    MODEL_CONFIDENCE = "MODEL_CONFIDENCE"
    SCENARIO_STABILITY = "SCENARIO_STABILITY"
    OUTCOME_HISTORY = "OUTCOME_HISTORY"


class DecisionTrustBand(str, Enum):
    HIGH_TRUST = "HIGH_TRUST"  # 90-100
    TRUSTED = "TRUSTED"        # 70-89
    RESTRICTED = "RESTRICTED"  # 50-69
    UNTRUSTED = "UNTRUSTED"    # <50


class DecisionTrustScore(BaseModel):
    score_id: str = Field(default_factory=lambda: f"dectrust_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    context_id: str
    overall_score: float
    trust_band: DecisionTrustBand
    dimension_scores: Dict[DecisionTrustDimension, float] = Field(default_factory=dict)
    calculated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DecisionTrustEngine:
    """Calculates multi-dimensional trust scores for enterprise decisions."""

    def calculate_trust_score(
        self,
        tenant_id: str,
        context_id: str,
        evidence_quality: float = 90.0,
        data_trust: float = 90.0,
        architecture_trust: float = 90.0,
        compliance_trust: float = 90.0,
        portfolio_trust: float = 90.0,
        model_confidence: float = 90.0,
        scenario_stability: float = 90.0,
        outcome_history: float = 90.0,
    ) -> DecisionTrustScore:
        dims = {
            DecisionTrustDimension.EVIDENCE_QUALITY: evidence_quality,
            DecisionTrustDimension.DATA_TRUST: data_trust,
            DecisionTrustDimension.ARCHITECTURE_TRUST: architecture_trust,
            DecisionTrustDimension.COMPLIANCE_TRUST: compliance_trust,
            DecisionTrustDimension.PORTFOLIO_TRUST: portfolio_trust,
            DecisionTrustDimension.MODEL_CONFIDENCE: model_confidence,
            DecisionTrustDimension.SCENARIO_STABILITY: scenario_stability,
            DecisionTrustDimension.OUTCOME_HISTORY: outcome_history,
        }

        overall = sum(dims.values()) / len(dims)
        overall = max(0.0, min(100.0, overall))

        if overall >= 90.0:
            band = DecisionTrustBand.HIGH_TRUST
        elif overall >= 70.0:
            band = DecisionTrustBand.TRUSTED
        elif overall >= 50.0:
            band = DecisionTrustBand.RESTRICTED
        else:
            band = DecisionTrustBand.UNTRUSTED

        return DecisionTrustScore(
            tenant_id=tenant_id,
            context_id=context_id,
            overall_score=overall,
            trust_band=band,
            dimension_scores=dims,
        )
