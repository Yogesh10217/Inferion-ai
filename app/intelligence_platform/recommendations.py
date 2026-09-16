"""Idempotent Actionable Recommendation Engine."""

import logging
import uuid
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from app.intelligence_platform.exceptions import (
    RecommendationExpiredException,
    RecommendationNotFoundException,
    RecommendationStaleException,
)

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class RecommendationType(str, Enum):
    SCALE_RESOURCE = "SCALE_RESOURCE"
    ROLLBACK_DEPLOYMENT = "ROLLBACK_DEPLOYMENT"
    CHANGE_MODEL = "CHANGE_MODEL"
    REDUCE_COST = "REDUCE_COST"
    UPDATE_POLICY = "UPDATE_POLICY"
    ROTATE_CREDENTIAL = "ROTATE_CREDENTIAL"
    RETRY_WORKFLOW = "RETRY_WORKFLOW"
    FAILOVER_SERVICE = "FAILOVER_SERVICE"
    REQUEST_HUMAN_REVIEW = "REQUEST_HUMAN_REVIEW"


class RecommendationPriority(str, Enum):
    P4_LOW = "P4_LOW"
    P3_MEDIUM = "P3_MEDIUM"
    P2_HIGH = "P2_HIGH"
    P1_CRITICAL = "P1_CRITICAL"


class RecommendationStatus(str, Enum):
    GENERATED = "GENERATED"
    VALIDATED = "VALIDATED"
    REQUIRES_APPROVAL = "REQUIRES_APPROVAL"
    APPROVED = "APPROVED"
    EXECUTING = "EXECUTING"
    EXECUTED = "EXECUTED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"
    SUPERSEDED = "SUPERSEDED"
    STALE = "STALE"


class Recommendation(BaseModel):
    recommendation_id: str = Field(default_factory=lambda: f"rec_{uuid.uuid4().hex[:10]}")
    tenant_id: str = "global"
    idempotency_key: str = Field(default_factory=lambda: f"idem_{uuid.uuid4().hex[:10]}")
    recommendation_type: RecommendationType
    priority: RecommendationPriority = RecommendationPriority.P3_MEDIUM
    status: RecommendationStatus = RecommendationStatus.GENERATED
    title: str
    action_description: str
    target_resource_id: str
    expected_impact: str
    confidence_score: float = 0.90
    risk_level: str = "LOW"
    execution_attempts: int = 0
    superseded_by: Optional[str] = None
    created_at: datetime = Field(default_factory=_now)
    expires_at: datetime = Field(default_factory=lambda: _now() + timedelta(hours=24))


class RecommendationManager:
    """Manages recommendations with idempotency, expiry, and superseding support."""

    def __init__(self) -> None:
        self._recommendations: Dict[str, Recommendation] = {}
        self._idempotency_map: Dict[str, str] = {}

    def create_recommendation(
        self,
        tenant_id: str,
        recommendation_type: RecommendationType,
        title: str,
        action_description: str,
        target_resource_id: str,
        expected_impact: str,
        priority: RecommendationPriority = RecommendationPriority.P3_MEDIUM,
        confidence_score: float = 0.90,
        risk_level: str = "LOW",
        idempotency_key: Optional[str] = None,
        ttl_hours: int = 24,
    ) -> Recommendation:
        idem_key = idempotency_key or f"idem_{tenant_id}_{target_resource_id}_{recommendation_type.value}"

        # Idempotency check
        if idem_key in self._idempotency_map:
            existing_id = self._idempotency_map[idem_key]
            existing_rec = self._recommendations.get(existing_id)
            if existing_rec and existing_rec.status not in (RecommendationStatus.EXPIRED, RecommendationStatus.SUPERSEDED):
                logger.info(f"[RECOMMENDATION MANAGER] Idempotent hit for key '{idem_key}', returning recommendation '{existing_rec.recommendation_id}'")
                return existing_rec

        expires_at = _now() + timedelta(hours=ttl_hours)

        rec = Recommendation(
            tenant_id=tenant_id,
            idempotency_key=idem_key,
            recommendation_type=recommendation_type,
            priority=priority,
            title=title,
            action_description=action_description,
            target_resource_id=target_resource_id,
            expected_impact=expected_impact,
            confidence_score=confidence_score,
            risk_level=risk_level,
            expires_at=expires_at,
        )

        self._recommendations[rec.recommendation_id] = rec
        self._idempotency_map[idem_key] = rec.recommendation_id
        logger.info(f"[RECOMMENDATION MANAGER] Created recommendation '{rec.recommendation_id}' ({recommendation_type.value}) for tenant '{tenant_id}'")
        return rec

    def supersede_recommendation(self, old_rec_id: str, new_rec_id: str, tenant_id: str) -> None:
        old_rec = self.get_recommendation(old_rec_id, tenant_id)
        old_rec.status = RecommendationStatus.SUPERSEDED
        old_rec.superseded_by = new_rec_id

    def update_status(self, recommendation_id: str, tenant_id: str, new_status: RecommendationStatus) -> Recommendation:
        rec = self.get_recommendation(recommendation_id, tenant_id)

        if _now() > rec.expires_at and new_status not in (RecommendationStatus.EXPIRED, RecommendationStatus.REJECTED):
            rec.status = RecommendationStatus.EXPIRED
            raise RecommendationExpiredException(f"Recommendation '{recommendation_id}' has expired.")

        if rec.status == RecommendationStatus.SUPERSEDED:
            raise RecommendationStaleException(f"Recommendation '{recommendation_id}' has been superseded.")

        rec.status = new_status
        return rec

    def get_recommendation(self, recommendation_id: str, tenant_id: str) -> Recommendation:
        rec = self._recommendations.get(recommendation_id)
        if not rec or rec.tenant_id != tenant_id:
            raise RecommendationNotFoundException(recommendation_id)
        return rec

    def list_recommendations(self, tenant_id: str, status: Optional[RecommendationStatus] = None) -> List[Recommendation]:
        res = [r for r in self._recommendations.values() if r.tenant_id == tenant_id]
        if status:
            res = [r for r in res if r.status == status]
        return res
