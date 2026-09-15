"""Security Trust Engine Subsystem (Phase 5.32)."""

from datetime import datetime, timezone
from pydantic import BaseModel, Field

from app.platform_contracts.trust import TrustAssessment
from app.platform_contracts.adapters import TrustAssessmentAdapter


class SecurityTrustDimension(BaseModel):
    name: str
    score: float = 90.0


class SecurityTrustScore(BaseModel):

    asset_id: str
    tenant_id: str
    score: float  # 0.0 to 100.0
    threat_free_score: float = 95.0
    vulnerability_remediation_score: float = 90.0
    calculated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class SecurityTrustEngine:
    """Computes security trust scores and adapts to TrustAssessment contract."""

    def compute_trust_score(
        self,
        tenant_id: str,
        asset_id: str,
        posture_score: float = 85.0,
    ) -> SecurityTrustScore:
        score = min(100.0, posture_score)
        return SecurityTrustScore(
            tenant_id=tenant_id,
            asset_id=asset_id,
            score=round(score, 2),
        )

    def to_contract_assessment(self, trust_score: SecurityTrustScore) -> TrustAssessment:
        return TrustAssessmentAdapter.from_domain_trust(
            tenant_id=trust_score.tenant_id,
            subject_type="SECURITY_ASSET",
            subject_id=trust_score.asset_id,
            score=trust_score.score,
        )
