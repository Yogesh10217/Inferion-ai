"""Commitment & Reservation Intelligence (Phase 5.42)."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, Optional

from pydantic import BaseModel, Field

from app.finops_intelligence.exceptions import (
    CrossTenantFinOpsIntelligenceException,
)


class CommitmentRisk(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class CommitmentRecommendation(BaseModel):
    recommendation_id: str = Field(default_factory=lambda: f"cmt_rec_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    resource_type: str  # GPU_RESERVATION, CLOUD_SAVINGS_PLAN, RESERVED_INSTANCE
    term_months: int = 12
    commitment_cost_usd: float = 10000.0
    estimated_savings_usd: float = 3000.0
    risk: CommitmentRisk = CommitmentRisk.MEDIUM
    requires_approval: bool = True
    approval_id: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CommitmentAssessment(BaseModel):
    tenant_id: str
    total_recommendations: int
    total_potential_savings_usd: float


class CommitmentManager:
    """Manages long-term capacity commitment and savings plan recommendations."""

    def __init__(self) -> None:
        self._recommendations: Dict[str, CommitmentRecommendation] = {}

    def recommend_commitment(
        self,
        tenant_id: str,
        resource_type: str,
        term_months: int,
        commitment_cost_usd: float,
        estimated_savings_usd: float,
        risk: CommitmentRisk = CommitmentRisk.MEDIUM,
    ) -> CommitmentRecommendation:
        is_high_risk = risk == CommitmentRisk.HIGH or commitment_cost_usd >= 50000.0
        rec = CommitmentRecommendation(
            tenant_id=tenant_id,
            resource_type=resource_type,
            term_months=term_months,
            commitment_cost_usd=commitment_cost_usd,
            estimated_savings_usd=estimated_savings_usd,
            risk=risk,
            requires_approval=is_high_risk,
        )
        self._recommendations[rec.recommendation_id] = rec
        return rec

    def approve_commitment(self, tenant_id: str, recommendation_id: str, approval_id: str = "appr_cmt_99") -> CommitmentRecommendation:
        rec = self.get_recommendation(tenant_id, recommendation_id)
        rec.approval_id = approval_id
        return rec

    def get_recommendation(self, tenant_id: str, recommendation_id: str) -> CommitmentRecommendation:
        rec = self._recommendations.get(recommendation_id)
        if not rec or rec.tenant_id != tenant_id:
            raise CrossTenantFinOpsIntelligenceException()
        return rec
