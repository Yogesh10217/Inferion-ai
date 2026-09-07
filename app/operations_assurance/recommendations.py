"""Operational recommendation intelligence (Advisory only - auto_execute=False mandatory)."""

from datetime import datetime, timezone
from enum import Enum
from typing import Dict, Any, List, Optional
import uuid
from pydantic import BaseModel, Field

from app.operations_assurance.exceptions import CrossTenantOperationsAssuranceException, OperationalRecommendationNotFoundException


class OperationalRecommendationType(str, Enum):
    INVESTIGATE_DEPENDENCY = "INVESTIGATE_DEPENDENCY"
    INCREASE_CAPACITY_RECOMMENDATION = "INCREASE_CAPACITY_RECOMMENDATION"
    REVIEW_CONFIGURATION = "REVIEW_CONFIGURATION"
    TRIGGER_ROLLBACK_REQUEST = "TRIGGER_ROLLBACK_REQUEST"
    REVIEW_MODEL = "REVIEW_MODEL"
    REVIEW_DATA_PIPELINE = "REVIEW_DATA_PIPELINE"
    ESCALATE_INCIDENT = "ESCALATE_INCIDENT"


class OperationalRecommendation(BaseModel):
    recommendation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    service_id: str
    recommendation_type: OperationalRecommendationType
    title: str
    description: str
    priority: str = "HIGH"
    auto_execute: bool = False  # Mandatory invariant: auto_execute = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class OperationalRecommendationManager:
    """Generates and manages advisory operational recommendations."""

    def __init__(self) -> None:
        self._recommendations: Dict[str, Dict[str, OperationalRecommendation]] = {}  # tenant_id -> {rec_id: rec}

    def create_recommendation(
        self,
        tenant_id: str,
        service_id: str,
        recommendation_type: OperationalRecommendationType,
        title: str,
        description: str,
        priority: str = "HIGH",
    ) -> OperationalRecommendation:
        rec = OperationalRecommendation(
            tenant_id=tenant_id,
            service_id=service_id,
            recommendation_type=recommendation_type,
            title=title,
            description=description,
            priority=priority,
            auto_execute=False,  # Enforce advisory invariant!
        )
        if tenant_id not in self._recommendations:
            self._recommendations[tenant_id] = {}
        self._recommendations[tenant_id][rec.recommendation_id] = rec
        return rec

    def list_recommendations(self, tenant_id: str, service_id: Optional[str] = None) -> List[OperationalRecommendation]:
        tenant_recs = self._recommendations.get(tenant_id, {})
        if service_id:
            return [r for r in tenant_recs.values() if r.service_id == service_id]
        return list(tenant_recs.values())

    def get_recommendation(self, tenant_id: str, recommendation_id: str) -> OperationalRecommendation:
        if tenant_id not in self._recommendations or recommendation_id not in self._recommendations[tenant_id]:
            for tid, recs in self._recommendations.items():
                if tid != tenant_id and recommendation_id in recs:
                    raise CrossTenantOperationsAssuranceException("Access denied.")
            raise OperationalRecommendationNotFoundException("Operational recommendation not found.")
        return self._recommendations[tenant_id][recommendation_id]
