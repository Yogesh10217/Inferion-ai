"""Data freshness intelligence (Phase 5.43)."""

import uuid
from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone, timedelta
from pydantic import BaseModel, Field

from app.data_intelligence.exceptions import CrossTenantDataIntelligenceException


class FreshnessStatus(str, Enum):
    FRESH = "FRESH"
    LAGGING = "LAGGING"
    STALE = "STALE"
    CRITICAL_STALE = "CRITICAL_STALE"


class FreshnessPolicy(BaseModel):
    policy_id: str
    dataset_id: str
    tenant_id: str
    expected_interval_minutes: int = 60
    max_allowed_delay_minutes: int = 120
    sla_hours: float = 24.0


class DataFreshness(BaseModel):
    freshness_id: str
    dataset_id: str
    tenant_id: str
    last_updated_at: datetime
    age_minutes: float
    status: FreshnessStatus
    is_sla_violated: bool = False


class FreshnessAssessment(BaseModel):
    assessment_id: str
    dataset_id: str
    tenant_id: str
    freshness: DataFreshness
    policy: FreshnessPolicy
    freshness_score: float  # 0.0 - 1.0 score influencing trust
    summary: str
    assessed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DataFreshnessManager:
    """Manages freshness evaluation without mutating or deleting underlying data."""

    def __init__(self) -> None:
        self._policies: Dict[str, FreshnessPolicy] = {}
        self._assessments: Dict[str, FreshnessAssessment] = {}

    def set_policy(
        self,
        dataset_id: str,
        tenant_id: str,
        expected_interval_minutes: int = 60,
        max_allowed_delay_minutes: int = 120,
        sla_hours: float = 24.0,
        policy_id: Optional[str] = None,
    ) -> FreshnessPolicy:
        pid = policy_id or f"fp-{uuid.uuid4().hex[:8]}"
        pol = FreshnessPolicy(
            policy_id=pid,
            dataset_id=dataset_id,
            tenant_id=tenant_id,
            expected_interval_minutes=expected_interval_minutes,
            max_allowed_delay_minutes=max_allowed_delay_minutes,
            sla_hours=sla_hours,
        )
        self._policies[dataset_id] = pol
        return pol

    def evaluate_freshness(
        self,
        dataset_id: str,
        tenant_id: str,
        last_updated_at: Optional[datetime] = None,
    ) -> FreshnessAssessment:
        policy = self._policies.get(dataset_id) or FreshnessPolicy(
            policy_id=f"fp-default-{dataset_id}",
            dataset_id=dataset_id,
            tenant_id=tenant_id,
        )

        now = datetime.now(timezone.utc)
        last_update = last_updated_at or (now - timedelta(minutes=30))
        age_mins = max(0.0, (now - last_update).total_seconds() / 60.0)

        if age_mins <= policy.expected_interval_minutes:
            status = FreshnessStatus.FRESH
            score = 1.0
            sla_violated = False
        elif age_mins <= policy.max_allowed_delay_minutes:
            status = FreshnessStatus.LAGGING
            score = 0.8
            sla_violated = False
        elif age_mins <= policy.sla_hours * 60.0:
            status = FreshnessStatus.STALE
            score = 0.4
            sla_violated = False
        else:
            status = FreshnessStatus.CRITICAL_STALE
            score = 0.1
            sla_violated = True

        fid = f"df-{uuid.uuid4().hex[:8]}"
        df = DataFreshness(
            freshness_id=fid,
            dataset_id=dataset_id,
            tenant_id=tenant_id,
            last_updated_at=last_update,
            age_minutes=round(age_mins, 2),
            status=status,
            is_sla_violated=sla_violated,
        )

        aid = f"fa-{uuid.uuid4().hex[:8]}"
        ass = FreshnessAssessment(
            assessment_id=aid,
            dataset_id=dataset_id,
            tenant_id=tenant_id,
            freshness=df,
            policy=policy,
            freshness_score=score,
            summary=f"Freshness for dataset {dataset_id}: status={status.value}, age={age_mins:.1f}m, score={score:.2f}",
        )
        self._assessments[aid] = ass
        return ass

    def get_assessment(self, assessment_id: str, tenant_id: str) -> FreshnessAssessment:
        ass = self._assessments.get(assessment_id)
        if not ass:
            raise Exception(f"Freshness assessment '{assessment_id}' not found.")
        if ass.tenant_id != tenant_id:
            raise CrossTenantDataIntelligenceException()
        return ass
