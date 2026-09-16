"""Control Assurance Trust Engine Subsystem (Phase 5.38)."""

import uuid
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field

from app.platform_contracts.tenant import TenantAccessGuard


class TrustBand(str, Enum):
    HIGH_TRUST = "HIGH_TRUST"
    MODERATE_TRUST = "MODERATE_TRUST"
    LOW_TRUST = "LOW_TRUST"


class ControlTrustDimension(str, Enum):
    CONTROL_EFFECTIVENESS = "CONTROL_EFFECTIVENESS"
    EVIDENCE_INTEGRITY = "EVIDENCE_INTEGRITY"
    EVALUATION_CONFIDENCE = "EVALUATION_CONFIDENCE"
    REMEDIATION_CONFIDENCE = "REMEDIATION_CONFIDENCE"
    ATTESTATION_CONFIDENCE = "ATTESTATION_CONFIDENCE"


class ControlTrustFactor(BaseModel):
    dimension: ControlTrustDimension
    score: float = 95.0
    weight: float = 1.0


class ControlAssuranceTrustScore(BaseModel):
    score_id: str = Field(default_factory=lambda: f"ctrust_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    control_id: str
    score: float = 92.5
    band: TrustBand = TrustBand.HIGH_TRUST
    factors: List[ControlTrustFactor] = Field(default_factory=list)


class ControlAssuranceTrustEngine:
    """Calculates control assurance trust scores adapted to TrustAssessment."""

    def __init__(self, tenant_guard: Optional[TenantAccessGuard] = None) -> None:
        self.tenant_guard = tenant_guard or TenantAccessGuard()

    def calculate_control_trust(self, tenant_id: str, control_id: str, is_degraded: bool = False) -> ControlAssuranceTrustScore:
        score = 45.0 if is_degraded else 92.5
        band = TrustBand.LOW_TRUST if is_degraded else TrustBand.HIGH_TRUST

        factors = [
            ControlTrustFactor(dimension=ControlTrustDimension.CONTROL_EFFECTIVENESS, score=score),
            ControlTrustFactor(dimension=ControlTrustDimension.EVIDENCE_INTEGRITY, score=98.0),
        ]

        return ControlAssuranceTrustScore(
            tenant_id=tenant_id,
            control_id=control_id,
            score=score,
            band=band,
            factors=factors,
        )
