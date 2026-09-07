"""Security Impact Assessment Engine."""

from typing import Dict, Any, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field


class SecurityImpactScore(BaseModel):
    impact_id: str = Field(default_factory=lambda: f"impact-{uuid.uuid4().hex[:8]}")
    tenant_id: str
    target_id: str
    confidentiality_impact: float = 0.0  # 0 to 10
    integrity_impact: float = 0.0  # 0 to 10
    availability_impact: float = 0.0  # 0 to 10
    overall_impact_score: float = 0.0  # 0 to 10
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class SecurityImpactEngine:
    """Calculates CIA security impact score for assets or incidents."""

    def evaluate_impact(self, tenant_id: str, target_id: str, c: float = 5.0, i: float = 5.0, a: float = 5.0) -> SecurityImpactScore:
        overall = round((c + i + a) / 3.0, 2)
        return SecurityImpactScore(
            tenant_id=tenant_id,
            target_id=target_id,
            confidentiality_impact=c,
            integrity_impact=i,
            availability_impact=a,
            overall_impact_score=overall,
        )
