"""Access Trust Engine (Phase 5.39)."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List

from pydantic import BaseModel, Field

from app.access_intelligence.exceptions import CrossTenantAccessIntelligenceException
from app.platform_contracts.trust import TrustAssessment, TrustBand, TrustConfidence
from app.platform_contracts.trust import TrustDimension as GenericTrustDimension


class AccessTrustDimension(str, Enum):
    IDENTITY_AUTHENTICATION = "IDENTITY_AUTHENTICATION"
    ENTITLEMENT_HYGIENE = "ENTITLEMENT_HYGIENE"
    ANOMALY_FREQUENCY = "ANOMALY_FREQUENCY"
    CERTIFICATION_COMPLIANCE = "CERTIFICATION_COMPLIANCE"
    SOD_COMPLIANCE = "SOD_COMPLIANCE"


class AccessTrustFactor(BaseModel):
    dimension: AccessTrustDimension
    score: float  # 0.0 to 100.0
    weight: float = 1.0
    notes: str = ""


class AccessTrustScore(BaseModel):
    """Access Trust Score Representation."""

    score_id: str = Field(default_factory=lambda: f"ats_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    target_identity_id: str
    overall_score: float = 100.0
    band: TrustBand = TrustBand.HIGH_TRUST
    factors: List[AccessTrustFactor] = Field(default_factory=list)
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AccessTrustEngine:
    """Evaluates access trust and adapts results to standard TrustAssessment."""

    def __init__(self) -> None:
        self._scores: Dict[str, AccessTrustScore] = {}

    def evaluate_identity_trust(
        self,
        tenant_id: str,
        identity_id: str,
        auth_score: float = 95.0,
        entitlement_hygiene_score: float = 90.0,
        anomaly_score: float = 100.0,
        certification_score: float = 100.0,
        sod_score: float = 100.0,
    ) -> TrustAssessment:
        factors = [
            AccessTrustFactor(dimension=AccessTrustDimension.IDENTITY_AUTHENTICATION, score=auth_score, weight=1.0),
            AccessTrustFactor(
                dimension=AccessTrustDimension.ENTITLEMENT_HYGIENE, score=entitlement_hygiene_score, weight=1.2
            ),
            AccessTrustFactor(dimension=AccessTrustDimension.ANOMALY_FREQUENCY, score=anomaly_score, weight=1.5),
            AccessTrustFactor(
                dimension=AccessTrustDimension.CERTIFICATION_COMPLIANCE, score=certification_score, weight=1.0
            ),
            AccessTrustFactor(dimension=AccessTrustDimension.SOD_COMPLIANCE, score=sod_score, weight=1.5),
        ]

        total_weighted = sum(f.score * f.weight for f in factors)
        total_weight = sum(f.weight for f in factors)
        composite = round(total_weighted / total_weight, 2) if total_weight > 0 else 0.0

        if composite >= 90.0:
            band = TrustBand.HIGH_TRUST
        elif composite >= 70.0:
            band = TrustBand.TRUSTED
        elif composite >= 50.0:
            band = TrustBand.RESTRICTED
        else:
            band = TrustBand.UNTRUSTED

        ats = AccessTrustScore(
            tenant_id=tenant_id,
            target_identity_id=identity_id,
            overall_score=composite,
            band=band,
            factors=factors,
        )
        self._scores[ats.score_id] = ats

        # Adapt to standard Platform Contract TrustAssessment
        generic_dims = [
            GenericTrustDimension(dimension_name=f.dimension.value, score=f.score, weight=f.weight) for f in factors
        ]

        assessment = TrustAssessment(
            subject_type="ACCESS_IDENTITY",
            subject_id=identity_id,
            tenant_id=tenant_id,
            score=composite,
            band=band,
            confidence=TrustConfidence.HIGH,
            dimensions=generic_dims,
        )
        return assessment

    def get_score(self, tenant_id: str, score_id: str) -> AccessTrustScore:
        ats = self._scores.get(score_id)
        if not ats or ats.tenant_id != tenant_id:
            raise CrossTenantAccessIntelligenceException()
        return ats
