"""Data Trust Engine & Multidimensional Trust Assessment Subsystem."""

from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field


class TrustDimension(str, Enum):
    QUALITY = "QUALITY"
    FRESHNESS = "FRESHNESS"
    LINEAGE_COMPLETENESS = "LINEAGE_COMPLETENESS"
    SOURCE_RELIABILITY = "SOURCE_RELIABILITY"
    CONTRACT_COMPLIANCE = "CONTRACT_COMPLIANCE"
    SECURITY_COMPLIANCE = "SECURITY_COMPLIANCE"
    PRIVACY_COMPLIANCE = "PRIVACY_COMPLIANCE"
    USAGE_HISTORY = "USAGE_HISTORY"


class TrustBand(str, Enum):
    HIGH_TRUST = "HIGH_TRUST"        # 90-100
    TRUSTED = "TRUSTED"              # 70-89
    RESTRICTED = "RESTRICTED"        # 50-69
    UNTRUSTED = "UNTRUSTED"          # <50


class DataTrustScore(BaseModel):
    score_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    asset_id: str
    overall_score: float  # 0.0 - 100.0
    trust_band: TrustBand
    dimension_scores: Dict[TrustDimension, float] = Field(default_factory=dict)
    factors: List[Dict[str, Any]] = Field(default_factory=list)
    calculated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DataTrustEngine:
    """Calculates multidimensional Data Trust Scores and provides Decision Intelligence trust factors."""

    def __init__(self) -> None:
        self._trust_cache: Dict[str, DataTrustScore] = {}

    def calculate_trust_score(
        self,
        tenant_id: str,
        asset_id: str,
        quality_score: float = 90.0,
        freshness_score: float = 85.0,
        lineage_score: float = 80.0,
        source_reliability: float = 95.0,
        contract_compliance: float = 100.0,
        security_compliance: float = 95.0,
        privacy_compliance: float = 100.0,
        usage_history: float = 90.0,
    ) -> DataTrustScore:
        dimension_scores = {
            TrustDimension.QUALITY: quality_score,
            TrustDimension.FRESHNESS: freshness_score,
            TrustDimension.LINEAGE_COMPLETENESS: lineage_score,
            TrustDimension.SOURCE_RELIABILITY: source_reliability,
            TrustDimension.CONTRACT_COMPLIANCE: contract_compliance,
            TrustDimension.SECURITY_COMPLIANCE: security_compliance,
            TrustDimension.PRIVACY_COMPLIANCE: privacy_compliance,
            TrustDimension.USAGE_HISTORY: usage_history,
        }

        # Weighted calculation
        weights = {
            TrustDimension.QUALITY: 0.20,
            TrustDimension.SECURITY_COMPLIANCE: 0.15,
            TrustDimension.PRIVACY_COMPLIANCE: 0.15,
            TrustDimension.CONTRACT_COMPLIANCE: 0.15,
            TrustDimension.LINEAGE_COMPLETENESS: 0.10,
            TrustDimension.FRESHNESS: 0.10,
            TrustDimension.SOURCE_RELIABILITY: 0.10,
            TrustDimension.USAGE_HISTORY: 0.05,
        }

        overall = sum(dimension_scores[dim] * weights[dim] for dim in dimension_scores)
        overall = max(0.0, min(100.0, overall))

        if overall >= 90.0:
            band = TrustBand.HIGH_TRUST
        elif overall >= 70.0:
            band = TrustBand.TRUSTED
        elif overall >= 50.0:
            band = TrustBand.RESTRICTED
        else:
            band = TrustBand.UNTRUSTED

        factors = [
            {"dimension": dim.value, "score": score, "weight": weights[dim]}
            for dim, score in dimension_scores.items()
        ]

        trust_score = DataTrustScore(
            tenant_id=tenant_id,
            asset_id=asset_id,
            overall_score=overall,
            trust_band=band,
            dimension_scores=dimension_scores,
            factors=factors,
        )
        self._trust_cache[asset_id] = trust_score
        return trust_score

    def get_trust_score(self, asset_id: str, tenant_id: str) -> DataTrustScore:
        if asset_id in self._trust_cache:
            return self._trust_cache[asset_id]
        return self.calculate_trust_score(tenant_id=tenant_id, asset_id=asset_id)

    def evaluate_ai_decision_trust(
        self,
        data_trust_score: float,
        decision_trust_score: float,
        risk_level: str,
    ) -> Dict[str, Any]:
        """Combine Data Trust × Decision Trust × Risk Level for Enterprise Intelligence (Phase 5.24 integration)."""
        composite_trust = (data_trust_score * 0.5) + (decision_trust_score * 0.5)

        if composite_trust >= 85.0 and risk_level in ("LOW", "MEDIUM"):
            action = "AUTONOMOUS"
        elif composite_trust >= 60.0 or risk_level == "MEDIUM":
            action = "APPROVAL_REQUIRED"
        else:
            action = "BLOCK"

        return {
            "composite_trust_score": composite_trust,
            "data_trust_score": data_trust_score,
            "decision_trust_score": decision_trust_score,
            "risk_level": risk_level,
            "recommended_action": action,
        }
