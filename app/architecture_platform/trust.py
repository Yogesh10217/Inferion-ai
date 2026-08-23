"""Architecture Trust Engine & Multidimensional Trust Assessment Subsystem."""

from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field


class ArchitectureTrustDimension(str, Enum):
    DEPENDENCY_HEALTH = "DEPENDENCY_HEALTH"
    ARCHITECTURE_COMPLIANCE = "ARCHITECTURE_COMPLIANCE"
    DRIFT_STATUS = "DRIFT_STATUS"
    RESILIENCE = "RESILIENCE"
    GOVERNANCE_COMPLIANCE = "GOVERNANCE_COMPLIANCE"
    SECURITY_POSTURE = "SECURITY_POSTURE"
    DATA_TRUST = "DATA_TRUST"
    OPERATIONAL_RELIABILITY = "OPERATIONAL_RELIABILITY"


class ArchitectureTrustBand(str, Enum):
    HIGH_TRUST = "HIGH_TRUST"   # 90-100
    TRUSTED = "TRUSTED"         # 70-89
    RESTRICTED = "RESTRICTED"   # 50-69
    UNTRUSTED = "UNTRUSTED"     # <50


class ArchitectureTrustScore(BaseModel):
    score_id: str = Field(default_factory=lambda: f"archtrust_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    overall_score: float  # 0.0 - 100.0
    trust_band: ArchitectureTrustBand
    dimension_scores: Dict[ArchitectureTrustDimension, float] = Field(default_factory=dict)
    calculated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ArchitectureTrustEngine:
    """Calculates Architecture Trust Scores and influences risk and change approval decisions."""

    def __init__(self) -> None:
        self._trust_cache: Dict[str, ArchitectureTrustScore] = {}

    def calculate_trust_score(
        self,
        tenant_id: str,
        dependency_health: float = 90.0,
        architecture_compliance: float = 95.0,
        drift_status_score: float = 85.0,
        resilience_score: float = 80.0,
        governance_compliance: float = 95.0,
        security_posture: float = 90.0,
        data_trust: float = 90.0,
        operational_reliability: float = 95.0,
    ) -> ArchitectureTrustScore:
        dimension_scores = {
            ArchitectureTrustDimension.DEPENDENCY_HEALTH: dependency_health,
            ArchitectureTrustDimension.ARCHITECTURE_COMPLIANCE: architecture_compliance,
            ArchitectureTrustDimension.DRIFT_STATUS: drift_status_score,
            ArchitectureTrustDimension.RESILIENCE: resilience_score,
            ArchitectureTrustDimension.GOVERNANCE_COMPLIANCE: governance_compliance,
            ArchitectureTrustDimension.SECURITY_POSTURE: security_posture,
            ArchitectureTrustDimension.DATA_TRUST: data_trust,
            ArchitectureTrustDimension.OPERATIONAL_RELIABILITY: operational_reliability,
        }

        weights = {
            ArchitectureTrustDimension.DEPENDENCY_HEALTH: 0.15,
            ArchitectureTrustDimension.ARCHITECTURE_COMPLIANCE: 0.15,
            ArchitectureTrustDimension.DRIFT_STATUS: 0.15,
            ArchitectureTrustDimension.RESILIENCE: 0.15,
            ArchitectureTrustDimension.GOVERNANCE_COMPLIANCE: 0.10,
            ArchitectureTrustDimension.SECURITY_POSTURE: 0.10,
            ArchitectureTrustDimension.DATA_TRUST: 0.10,
            ArchitectureTrustDimension.OPERATIONAL_RELIABILITY: 0.10,
        }

        overall = sum(dimension_scores[dim] * weights[dim] for dim in dimension_scores)
        overall = max(0.0, min(100.0, overall))

        if overall >= 90.0:
            band = ArchitectureTrustBand.HIGH_TRUST
        elif overall >= 70.0:
            band = ArchitectureTrustBand.TRUSTED
        elif overall >= 50.0:
            band = ArchitectureTrustBand.RESTRICTED
        else:
            band = ArchitectureTrustBand.UNTRUSTED

        score = ArchitectureTrustScore(
            tenant_id=tenant_id,
            overall_score=overall,
            trust_band=band,
            dimension_scores=dimension_scores,
        )
        self._trust_cache[tenant_id] = score
        return score

    def get_trust_score(self, tenant_id: str) -> ArchitectureTrustScore:
        if tenant_id in self._trust_cache:
            return self._trust_cache[tenant_id]
        return self.calculate_trust_score(tenant_id=tenant_id)
