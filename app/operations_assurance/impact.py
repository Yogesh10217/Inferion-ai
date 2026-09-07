"""Operational impact assessment across Technical, Service, Business, Financial, Security, Data, Model, and Customer dimensions."""

from datetime import datetime, timezone
from enum import Enum
from typing import Dict, Any, List, Optional
import uuid
from pydantic import BaseModel, Field


class ImpactDimension(str, Enum):
    TECHNICAL = "TECHNICAL"
    SERVICE = "SERVICE"
    BUSINESS = "BUSINESS"
    FINANCIAL = "FINANCIAL"
    SECURITY = "SECURITY"
    DATA = "DATA"
    MODEL = "MODEL"
    CUSTOMER = "CUSTOMER"


class OperationalImpactScore(BaseModel):
    assessment_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    target_id: str
    overall_impact_score: float = 0.5
    dimension_scores: Dict[ImpactDimension, float] = Field(default_factory=dict)
    financial_cost_estimate: float = 0.0
    customer_disruption_level: str = "LOW"
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class OperationsImpactEngine:
    """Evaluates multi-dimensional operational impact across technical and business domains."""

    def __init__(self) -> None:
        pass

    def evaluate_impact(
        self,
        tenant_id: str,
        target_id: str,
        technical_impact: float = 0.2,
        service_impact: float = 0.3,
        business_impact: float = 0.1,
        financial_cost: float = 0.0,
    ) -> OperationalImpactScore:
        dim_scores = {
            ImpactDimension.TECHNICAL: technical_impact,
            ImpactDimension.SERVICE: service_impact,
            ImpactDimension.BUSINESS: business_impact,
            ImpactDimension.FINANCIAL: min(1.0, financial_cost / 10000.0),
            ImpactDimension.SECURITY: 0.0,
            ImpactDimension.DATA: 0.0,
            ImpactDimension.MODEL: 0.0,
            ImpactDimension.CUSTOMER: service_impact,
        }
        overall = sum(dim_scores.values()) / len(dim_scores)

        return OperationalImpactScore(
            tenant_id=tenant_id,
            target_id=target_id,
            overall_impact_score=round(overall, 3),
            dimension_scores=dim_scores,
            financial_cost_estimate=financial_cost,
            customer_disruption_level="HIGH" if service_impact > 0.7 else ("MEDIUM" if service_impact > 0.3 else "LOW"),
        )
