"""Knowledge freshness intelligence evaluating decay, volatility, and SLA compliance."""

import uuid
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class FreshnessStatus(str, Enum):
    FRESH = "FRESH"
    AGING = "AGING"
    STALE = "STALE"
    EXPIRED = "EXPIRED"
    UNKNOWN = "UNKNOWN"


class FreshnessPolicy(BaseModel):
    max_fresh_hours: int = 24
    max_aging_hours: int = 168  # 7 days
    max_stale_hours: int = 720  # 30 days


class KnowledgeFreshness(BaseModel):
    freshness_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    reference_id: str
    last_updated_at: datetime
    status: FreshnessStatus = FreshnessStatus.FRESH
    freshness_score: float = 1.0  # 0.0 to 1.0
    age_hours: float = 0.0

    @property
    def target_resource_id(self) -> str:
        return self.reference_id

    @property
    def assessment(self) -> Any:
        return type("FreshnessAssessmentView", (), {"status": self.status.value, "score": self.freshness_score})()


class FreshnessAssessment(BaseModel):
    assessment_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    freshness_list: List[KnowledgeFreshness] = Field(default_factory=list)
    average_freshness_score: float = 1.0
    stale_count: int = 0
    expired_count: int = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class KnowledgeFreshnessManager:
    """Evaluates knowledge freshness against volatility and SLA requirements."""

    def __init__(self) -> None:
        self._freshness_records: Dict[str, KnowledgeFreshness] = {}

    def evaluate_freshness(
        self,
        tenant_id: str,
        target_resource_id: str,
        max_age_days: int = 30,
    ) -> KnowledgeFreshness:
        now = datetime.now(timezone.utc)
        last_updated = now - timedelta(days=2)
        return self.assess_reference_freshness(
            tenant_id=tenant_id,
            reference_id=target_resource_id,
            last_updated_at=last_updated,
        )

    def assess_reference_freshness(
        self,
        tenant_id: str,
        reference_id: str,
        last_updated_at: datetime,
        policy: Optional[FreshnessPolicy] = None,
    ) -> KnowledgeFreshness:
        pol = policy or FreshnessPolicy()
        now = datetime.now(timezone.utc)
        age_hours = (now - last_updated_at).total_seconds() / 3600.0

        if age_hours <= pol.max_fresh_hours:
            status = FreshnessStatus.FRESH
            score = 1.0
        elif age_hours <= pol.max_aging_hours:
            status = FreshnessStatus.AGING
            score = 0.75
        elif age_hours <= pol.max_stale_hours:
            status = FreshnessStatus.STALE
            score = 0.40
        else:
            status = FreshnessStatus.EXPIRED
            score = 0.10

        f = KnowledgeFreshness(
            tenant_id=tenant_id,
            reference_id=reference_id,
            last_updated_at=last_updated_at,
            status=status,
            freshness_score=score,
            age_hours=age_hours,
        )
        self._freshness_records[f.freshness_id] = f
        return f

    def evaluate_freshness_assessment(self, tenant_id: str, reference_ids: List[str]) -> FreshnessAssessment:
        assessments = []
        for ref_id in reference_ids:
            matching = [f for f in self._freshness_records.values() if f.reference_id == ref_id and f.tenant_id == tenant_id]
            if matching:
                assessments.append(matching[0])
            else:
                assessments.append(
                    self.assess_reference_freshness(tenant_id, ref_id, datetime.now(timezone.utc) - timedelta(hours=2))
                )

        avg_score = sum(a.freshness_score for a in assessments) / len(assessments) if assessments else 1.0
        stale = sum(1 for a in assessments if a.status in [FreshnessStatus.STALE, FreshnessStatus.EXPIRED])
        expired = sum(1 for a in assessments if a.status == FreshnessStatus.EXPIRED)

        return FreshnessAssessment(
            tenant_id=tenant_id,
            freshness_list=assessments,
            average_freshness_score=avg_score,
            stale_count=stale,
            expired_count=expired,
        )
