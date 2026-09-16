"""Security Recommendation Manager."""

import uuid
from datetime import datetime, timezone
from typing import Dict, List

from pydantic import BaseModel, Field


class SecurityRecommendation(BaseModel):
    recommendation_id: str = Field(default_factory=lambda: f"sec-rec-{uuid.uuid4().hex[:8]}")
    tenant_id: str
    title: str
    target_asset_id: str
    priority: str  # LOW, MEDIUM, HIGH, CRITICAL
    description: str
    suggested_action: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class SecurityRecommendationManager:
    """Generates actionable security hardening recommendations."""

    def __init__(self) -> None:
        self._recs: Dict[str, SecurityRecommendation] = {}

    def generate_recommendation(
        self,
        tenant_id: str,
        title: str,
        target_asset_id: str,
        priority: str = "HIGH",
        description: str = "",
        suggested_action: str = "",
    ) -> SecurityRecommendation:
        rec = SecurityRecommendation(
            tenant_id=tenant_id,
            title=title,
            target_asset_id=target_asset_id,
            priority=priority,
            description=description,
            suggested_action=suggested_action,
        )
        self._recs[rec.recommendation_id] = rec
        return rec

    def list_recommendations(self, tenant_id: str) -> List[SecurityRecommendation]:
        return [r for r in self._recs.values() if r.tenant_id == tenant_id]
