"""AI Cost Optimization Engine."""

import logging
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from typing import Any, Dict, List

from pydantic import BaseModel, Field, field_validator

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class OptimizationRiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class OptimizationActionType(str, Enum):
    CHEAPER_MODEL_ROUTING = "CHEAPER_MODEL_ROUTING"
    CACHE_RESPONSE = "CACHE_RESPONSE"
    PROMPT_COMPRESSION = "PROMPT_COMPRESSION"
    REDUCE_IDLE_WORKERS = "REDUCE_IDLE_WORKERS"
    PARALLELIZE_WORKFLOW = "PARALLELIZE_WORKFLOW"


class OptimizationRecommendation(BaseModel):
    recommendation_id: str = Field(default_factory=lambda: f"rec_{uuid.uuid4().hex[:10]}")
    tenant_id: str = "global"
    action_type: OptimizationActionType = OptimizationActionType.CHEAPER_MODEL_ROUTING
    risk_level: OptimizationRiskLevel = OptimizationRiskLevel.LOW

    estimated_monthly_savings: Decimal = Decimal("25.0")
    target_resource_id: str
    description: str = ""

    status: str = "PENDING"  # PENDING, APPROVED, APPLIED, REJECTED
    created_at: datetime = Field(default_factory=_now)

    @field_validator("estimated_monthly_savings", mode="before")
    @classmethod
    def parse_decimal(cls, value: Any) -> Decimal:
        if isinstance(value, float):
            return Decimal(str(value))
        return Decimal(value)


class CostOptimizationEngine:
    """Detects cost reduction opportunities across models, agents, workflows, and infrastructure."""

    def __init__(self) -> None:
        self._recommendations: Dict[str, OptimizationRecommendation] = {}

    def generate_recommendations(self, tenant_id: str = "global") -> List[OptimizationRecommendation]:
        recs = [
            OptimizationRecommendation(
                tenant_id=tenant_id,
                action_type=OptimizationActionType.CHEAPER_MODEL_ROUTING,
                risk_level=OptimizationRiskLevel.MEDIUM,
                estimated_monthly_savings=Decimal("45.50"),
                target_resource_id="agent_support_qa",
                description="Route non-critical QA queries to GPT-3.5-Turbo instead of GPT-4",
            ),
            OptimizationRecommendation(
                tenant_id=tenant_id,
                action_type=OptimizationActionType.CACHE_RESPONSE,
                risk_level=OptimizationRiskLevel.LOW,
                estimated_monthly_savings=Decimal("18.00"),
                target_resource_id="rag_docs_index",
                description="Cache repeated vector search embeddings for high-frequency queries",
            ),
        ]
        for r in recs:
            self._recommendations[r.recommendation_id] = r

        logger.info(f"[COST OPTIMIZATION] Generated {len(recs)} optimization recommendations for tenant '{tenant_id}'")
        return recs

    def get_recommendation(self, recommendation_id: str) -> OptimizationRecommendation:
        rec = self._recommendations.get(recommendation_id)
        if not rec:
            raise KeyError(f"Recommendation '{recommendation_id}' not found")
        return rec
