"""Cost Optimization Intelligence (Phase 5.42)."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List

from pydantic import BaseModel, Field

from app.finops_intelligence.exceptions import CrossTenantFinOpsIntelligenceException


class OptimizationType(str, Enum):
    MODEL_RIGHTSIZING = "MODEL_RIGHTSIZING"
    TOKEN_OPTIMIZATION = "TOKEN_OPTIMIZATION"  # nosec B105
    INFRASTRUCTURE_DOWNSIZING = "INFRASTRUCTURE_DOWNSIZING"
    IDLE_RESOURCE_CLEANUP = "IDLE_RESOURCE_CLEANUP"
    RESERVED_CAPACITY = "RESERVED_CAPACITY"


class OptimizationPriority(str, Enum):
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"
    P4 = "P4"


class OptimizationImpact(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class OptimizationStatus(str, Enum):
    PROPOSED = "PROPOSED"
    APPROVED = "APPROVED"
    DELEGATED = "DELEGATED"
    VERIFIED = "VERIFIED"
    REJECTED = "REJECTED"


class OptimizationRecommendation(BaseModel):
    optimization_id: str = Field(default_factory=lambda: f"opt_rec_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    target_resource_id: str
    optimization_type: OptimizationType = OptimizationType.MODEL_RIGHTSIZING
    estimated_monthly_savings_usd: float = 0.0
    priority: OptimizationPriority = OptimizationPriority.P2
    impact: OptimizationImpact = OptimizationImpact.MEDIUM
    status: OptimizationStatus = OptimizationStatus.PROPOSED
    is_high_risk: bool = False
    action_summary: str = ""
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CostOptimizationManager:
    """Manages non-mutating cost optimization recommendations."""

    def __init__(self) -> None:
        self._recommendations: Dict[str, OptimizationRecommendation] = {}

    def create_recommendation(
        self,
        tenant_id: str,
        target_resource_id: str,
        optimization_type: OptimizationType,
        estimated_monthly_savings_usd: float,
        action_summary: str,
        is_high_risk: bool = False,
        priority: OptimizationPriority = OptimizationPriority.P2,
    ) -> OptimizationRecommendation:
        rec = OptimizationRecommendation(
            tenant_id=tenant_id,
            target_resource_id=target_resource_id,
            optimization_type=optimization_type,
            estimated_monthly_savings_usd=estimated_monthly_savings_usd,
            action_summary=action_summary,
            is_high_risk=is_high_risk,
            priority=priority,
        )
        self._recommendations[rec.optimization_id] = rec
        return rec

    def approve_recommendation(self, tenant_id: str, optimization_id: str) -> OptimizationRecommendation:
        rec = self.get_recommendation(tenant_id, optimization_id)
        rec.status = OptimizationStatus.APPROVED
        return rec

    def get_recommendation(self, tenant_id: str, optimization_id: str) -> OptimizationRecommendation:
        rec = self._recommendations.get(optimization_id)
        if not rec or rec.tenant_id != tenant_id:
            raise CrossTenantFinOpsIntelligenceException()
        return rec

    def list_recommendations(self, tenant_id: str) -> List[OptimizationRecommendation]:
        return [r for r in self._recommendations.values() if r.tenant_id == tenant_id]
