"""Dataset trust intelligence engine (Phase 5.43)."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import List

from pydantic import BaseModel, Field

from app.platform_contracts.trust import TrustAssessment, TrustBand, TrustConfidence, TrustDimension


class DatasetTrustDimension(str, Enum):
    QUALITY = "QUALITY"
    FRESHNESS = "FRESHNESS"
    LINEAGE = "LINEAGE"
    RELIABILITY = "RELIABILITY"
    SECURITY_POSTURE = "SECURITY_POSTURE"
    COMPLIANCE = "COMPLIANCE"
    ANOMALY_STATUS = "ANOMALY_STATUS"


class DatasetTrustFactor(BaseModel):
    dimension: DatasetTrustDimension
    score: float
    weight: float = 1.0
    explanation: str


class DatasetTrustScore(BaseModel):
    dataset_id: str
    tenant_id: str
    overall_trust_score: float  # 0.0 - 100.0
    band: TrustBand
    factors: List[DatasetTrustFactor] = Field(default_factory=list)
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DatasetTrustEngine:
    """Evaluates explainable dataset trust scores and adapts results to platform TrustAssessment."""

    def evaluate_trust(
        self,
        dataset_id: str,
        tenant_id: str,
        quality_score: float = 0.95,
        freshness_score: float = 0.90,
        lineage_score: float = 1.0,
        reliability_score: float = 0.95,
        security_score: float = 0.90,
        compliance_score: float = 1.0,
        anomaly_score: float = 1.0,  # 1.0 = no anomalies
    ) -> TrustAssessment:
        factors = [
            DatasetTrustFactor(
                dimension=DatasetTrustDimension.QUALITY,
                score=round(quality_score * 100, 2),
                weight=1.5,
                explanation=f"Quality score: {quality_score:.2f}",
            ),
            DatasetTrustFactor(
                dimension=DatasetTrustDimension.FRESHNESS,
                score=round(freshness_score * 100, 2),
                weight=1.2,
                explanation=f"Freshness score: {freshness_score:.2f}",
            ),
            DatasetTrustFactor(
                dimension=DatasetTrustDimension.LINEAGE,
                score=round(lineage_score * 100, 2),
                weight=1.0,
                explanation=f"Lineage completeness: {lineage_score:.2f}",
            ),
            DatasetTrustFactor(
                dimension=DatasetTrustDimension.RELIABILITY,
                score=round(reliability_score * 100, 2),
                weight=1.0,
                explanation=f"Pipeline reliability: {reliability_score:.2f}",
            ),
            DatasetTrustFactor(
                dimension=DatasetTrustDimension.SECURITY_POSTURE,
                score=round(security_score * 100, 2),
                weight=1.0,
                explanation=f"Security posture: {security_score:.2f}",
            ),
            DatasetTrustFactor(
                dimension=DatasetTrustDimension.COMPLIANCE,
                score=round(compliance_score * 100, 2),
                weight=1.0,
                explanation=f"Compliance adherence: {compliance_score:.2f}",
            ),
            DatasetTrustFactor(
                dimension=DatasetTrustDimension.ANOMALY_STATUS,
                score=round(anomaly_score * 100, 2),
                weight=1.3,
                explanation=f"Anomaly status score: {anomaly_score:.2f}",
            ),
        ]

        total_weight = sum(f.weight for f in factors)
        weighted_score = sum(f.score * f.weight for f in factors) / max(0.001, total_weight)
        final_score = round(weighted_score, 2)

        band = (
            TrustBand.HIGH_TRUST
            if final_score >= 90.0
            else (
                TrustBand.TRUSTED
                if final_score >= 70.0
                else (TrustBand.RESTRICTED if final_score >= 50.0 else TrustBand.UNTRUSTED)
            )
        )

        dimensions_contract = [
            TrustDimension(dimension_name=f.dimension.value, score=f.score, weight=f.weight) for f in factors
        ]

        aid = f"trust-ds-{uuid.uuid4().hex[:12]}"
        return TrustAssessment(
            assessment_id=aid,
            subject_type="DATASET",
            subject_id=dataset_id,
            tenant_id=tenant_id,
            score=final_score,
            band=band,
            confidence=TrustConfidence.HIGH,
            dimensions=dimensions_contract,
        )
