"""Knowledge Freshness Intelligence Subsystem (Phase 5.35)."""

from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone, timedelta
import uuid
from pydantic import BaseModel, Field


class FreshnessStatus(str, Enum):
    FRESH = "FRESH"
    AGING = "AGING"
    STALE = "STALE"
    EXPIRED = "EXPIRED"
    UNKNOWN = "UNKNOWN"


class FreshnessPolicy(BaseModel):
    policy_id: str = Field(default_factory=lambda: f"freshpol_{uuid.uuid4().hex[:8]}")
    domain: str = "GENERAL"
    aging_threshold_days: int = 30
    stale_threshold_days: int = 90
    expired_threshold_days: int = 180


class KnowledgeFreshness(BaseModel):
    freshness_id: str = Field(default_factory=lambda: f"kfresh_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    item_id: str
    status: FreshnessStatus
    age_days: float
    last_updated_at: datetime
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class FreshnessEvaluation(BaseModel):
    item_id: str
    tenant_id: str
    freshness: KnowledgeFreshness
    trust_reduction_factor: float  # 0.0 to 1.0 multiplier
    action_recommendation: Optional[str] = None


class KnowledgeFreshnessManager:
    """Evaluates knowledge age, decay, and staleness without deleting historical knowledge."""

    def __init__(self) -> None:
        self._default_policy = FreshnessPolicy()

    def evaluate_freshness(
        self,
        tenant_id: str,
        item_id: str,
        last_updated_at: datetime,
        policy: Optional[FreshnessPolicy] = None,
    ) -> FreshnessEvaluation:
        pol = policy or self._default_policy
        now = datetime.now(timezone.utc)
        
        if last_updated_at.tzinfo is None:
            last_updated_at = last_updated_at.replace(tzinfo=timezone.utc)

        age_seconds = (now - last_updated_at).total_seconds()
        age_days = max(0.0, age_seconds / 86400.0)

        if age_days < pol.aging_threshold_days:
            status = FreshnessStatus.FRESH
            trust_factor = 1.0
            rec = None
        elif age_days < pol.stale_threshold_days:
            status = FreshnessStatus.AGING
            trust_factor = 0.85
            rec = "Consider reviewing knowledge freshness"
        elif age_days < pol.expired_threshold_days:
            status = FreshnessStatus.STALE
            trust_factor = 0.50
            rec = "Knowledge is stale. Revalidation recommended."
        else:
            status = FreshnessStatus.EXPIRED
            trust_factor = 0.20
            rec = "Knowledge is expired. Revalidation or retirement required."

        fresh = KnowledgeFreshness(
            tenant_id=tenant_id,
            item_id=item_id,
            status=status,
            age_days=round(age_days, 2),
            last_updated_at=last_updated_at,
        )

        return FreshnessEvaluation(
            item_id=item_id,
            tenant_id=tenant_id,
            freshness=fresh,
            trust_reduction_factor=trust_factor,
            action_recommendation=rec,
        )
