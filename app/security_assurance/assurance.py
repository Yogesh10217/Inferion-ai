"""Security Assurance Engine."""

import uuid
from datetime import datetime, timezone

from pydantic import BaseModel, Field


class SecurityAssuranceScore(BaseModel):
    score_id: str = Field(default_factory=lambda: f"sec-assur-{uuid.uuid4().hex[:8]}")
    tenant_id: str
    overall_score: float  # 0.0 to 100.0
    posture_factor: float
    threat_mitigation_factor: float
    governance_factor: float
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class SecurityAssuranceEngine:
    """Computes overall security assurance index score for a tenant."""

    def compute_assurance_score(
        self,
        tenant_id: str,
        posture_score: float = 100.0,
        unmitigated_threats: int = 0,
        unapproved_actions: int = 0,
    ) -> SecurityAssuranceScore:
        threat_deduction = unmitigated_threats * 15.0
        gov_deduction = unapproved_actions * 10.0
        overall = max(0.0, min(100.0, posture_score - threat_deduction - gov_deduction))

        return SecurityAssuranceScore(
            tenant_id=tenant_id,
            overall_score=round(overall, 2),
            posture_factor=posture_score,
            threat_mitigation_factor=100.0 - threat_deduction,
            governance_factor=100.0 - gov_deduction,
        )
