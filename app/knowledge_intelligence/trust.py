"""Knowledge Trust Evaluation Subsystem (Phase 5.35)."""

from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.platform_contracts.trust import (
    TrustAssessment,
    TrustBand,
    TrustConfidence,
    TrustDimension as ContractTrustDimension,
)
from app.platform_contracts.redaction import SensitiveDataSanitizer


class KnowledgeTrustDimension(str, Enum):
    SOURCE_RELIABILITY = "SOURCE_RELIABILITY"
    PROVENANCE_COMPLETENESS = "PROVENANCE_COMPLETENESS"
    EVIDENCE_STRENGTH = "EVIDENCE_STRENGTH"
    FRESHNESS = "FRESHNESS"
    CROSS_SOURCE_CONSISTENCY = "CROSS_SOURCE_CONSISTENCY"
    HUMAN_VALIDATION = "HUMAN_VALIDATION"
    INTEGRITY = "INTEGRITY"


class KnowledgeTrustFactor(BaseModel):
    dimension: KnowledgeTrustDimension
    score: float  # 0.0 - 100.0
    weight: float = 1.0
    reasoning: str = ""


class KnowledgeTrustScore(BaseModel):
    score_id: str = Field(default_factory=lambda: f"ktrust_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    item_id: str
    overall_score: float  # 0.0 - 100.0
    trust_band: TrustBand
    factors: List[KnowledgeTrustFactor] = Field(default_factory=list)
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class KnowledgeTrustEngine:
    """Evaluates multi-dimensional knowledge trust scores and adapts to TrustAssessment contract."""

    def evaluate_trust(
        self,
        tenant_id: str,
        item_id: str,
        is_fresh: bool = True,
        has_provenance: bool = True,
        evidence_count: int = 1,
        contradiction_count: int = 0,
    ) -> KnowledgeTrustScore:
        factors = []
        
        fresh_score = 95.0 if is_fresh else 40.0
        factors.append(KnowledgeTrustFactor(dimension=KnowledgeTrustDimension.FRESHNESS, score=fresh_score, reasoning="Freshness check"))

        prov_score = 90.0 if has_provenance else 30.0
        factors.append(KnowledgeTrustFactor(dimension=KnowledgeTrustDimension.PROVENANCE_COMPLETENESS, score=prov_score, reasoning="Provenance completeness"))

        ev_score = min(100.0, 60.0 + (evidence_count * 15.0))
        factors.append(KnowledgeTrustFactor(dimension=KnowledgeTrustDimension.EVIDENCE_STRENGTH, score=ev_score, reasoning="Evidence count"))

        cons_score = max(10.0, 95.0 - (contradiction_count * 35.0))
        factors.append(KnowledgeTrustFactor(dimension=KnowledgeTrustDimension.CROSS_SOURCE_CONSISTENCY, score=cons_score, reasoning="Contradiction impact"))

        total_weight = sum(f.weight for f in factors)
        weighted_sum = sum(f.score * f.weight for f in factors)
        overall = round(weighted_sum / total_weight if total_weight > 0 else 50.0, 2)

        if overall >= 90.0:
            band = TrustBand.HIGH_TRUST
        elif overall >= 70.0:
            band = TrustBand.TRUSTED
        elif overall >= 50.0:
            band = TrustBand.RESTRICTED
        else:
            band = TrustBand.UNTRUSTED

        score_obj = KnowledgeTrustScore(
            tenant_id=tenant_id,
            item_id=item_id,
            overall_score=overall,
            trust_band=band,
            factors=factors,
        )
        return score_obj

    def to_trust_assessment(self, trust_score: KnowledgeTrustScore) -> TrustAssessment:
        contract_dims = [
            ContractTrustDimension(
                dimension_name=f.dimension.value,
                score=f.score,
                weight=f.weight,
            )
            for f in trust_score.factors
        ]
        return TrustAssessment(
            subject_type="KNOWLEDGE_ITEM",
            subject_id=trust_score.item_id,
            tenant_id=trust_score.tenant_id,
            score=trust_score.overall_score,
            band=trust_score.trust_band,
            confidence=TrustConfidence.HIGH,
            dimensions=contract_dims,
            evidence_references=[f"ktrust_{trust_score.item_id}"],
        )
