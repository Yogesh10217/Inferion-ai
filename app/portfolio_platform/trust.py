"""Portfolio Trust & Confidence Engine Subsystem."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict

from pydantic import BaseModel, Field


class PortfolioTrustDimension(str, Enum):
    EVIDENCE_QUALITY = "EVIDENCE_QUALITY"
    COST_CONFIDENCE = "COST_CONFIDENCE"
    BENEFIT_CONFIDENCE = "BENEFIT_CONFIDENCE"
    DATA_TRUST = "DATA_TRUST"
    ARCHITECTURE_TRUST = "ARCHITECTURE_TRUST"
    COMPLIANCE_STATUS = "COMPLIANCE_STATUS"
    RISK_CONFIDENCE = "RISK_CONFIDENCE"
    HISTORICAL_OUTCOME_ACCURACY = "HISTORICAL_OUTCOME_ACCURACY"


class PortfolioTrustBand(str, Enum):
    HIGH_TRUST = "HIGH_TRUST"  # 90-100
    TRUSTED = "TRUSTED"        # 70-89
    RESTRICTED = "RESTRICTED"  # 50-69
    UNTRUSTED = "UNTRUSTED"    # <50


class PortfolioTrustScore(BaseModel):
    score_id: str = Field(default_factory=lambda: f"porttrust_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    overall_score: float
    trust_band: PortfolioTrustBand
    dimension_scores: Dict[PortfolioTrustDimension, float] = Field(default_factory=dict)
    calculated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class PortfolioTrustEngine:
    """Calculates multidimensional trust scores for enterprise AI portfolios."""

    def __init__(self) -> None:
        self._trust_cache: Dict[str, PortfolioTrustScore] = {}

    def calculate_trust_score(
        self,
        tenant_id: str,
        evidence_quality: float = 90.0,
        cost_confidence: float = 90.0,
        benefit_confidence: float = 90.0,
        data_trust: float = 95.0,
        architecture_trust: float = 90.0,
        compliance_status: float = 90.0,
        risk_confidence: float = 90.0,
        historical_accuracy: float = 90.0,
    ) -> PortfolioTrustScore:
        dim_scores = {
            PortfolioTrustDimension.EVIDENCE_QUALITY: evidence_quality,
            PortfolioTrustDimension.COST_CONFIDENCE: cost_confidence,
            PortfolioTrustDimension.BENEFIT_CONFIDENCE: benefit_confidence,
            PortfolioTrustDimension.DATA_TRUST: data_trust,
            PortfolioTrustDimension.ARCHITECTURE_TRUST: architecture_trust,
            PortfolioTrustDimension.COMPLIANCE_STATUS: compliance_status,
            PortfolioTrustDimension.RISK_CONFIDENCE: risk_confidence,
            PortfolioTrustDimension.HISTORICAL_OUTCOME_ACCURACY: historical_accuracy,
        }

        overall = sum(dim_scores.values()) / len(dim_scores)
        overall = max(0.0, min(100.0, overall))

        if overall >= 90.0:
            band = PortfolioTrustBand.HIGH_TRUST
        elif overall >= 70.0:
            band = PortfolioTrustBand.TRUSTED
        elif overall >= 50.0:
            band = PortfolioTrustBand.RESTRICTED
        else:
            band = PortfolioTrustBand.UNTRUSTED

        score = PortfolioTrustScore(
            tenant_id=tenant_id,
            overall_score=overall,
            trust_band=band,
            dimension_scores=dim_scores,
        )
        self._trust_cache[tenant_id] = score
        return score

    def get_trust_score(self, tenant_id: str) -> PortfolioTrustScore:
        if tenant_id in self._trust_cache:
            return self._trust_cache[tenant_id]
        return self.calculate_trust_score(tenant_id)
