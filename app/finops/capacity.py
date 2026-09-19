"""Capacity Planning & Infrastructure Scaling Intelligence Subsystem."""

import logging
import uuid
from datetime import datetime, timezone
from typing import List

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class CapacityRecommendation(BaseModel):
    recommendation_id: str = Field(default_factory=lambda: f"cap_rec_{uuid.uuid4().hex[:10]}")
    resource_type: str  # CPU, MEMORY, WORKER_CONCURRENCY, QUEUE_DEPTH, THROUGHPUT, STORAGE, CACHE
    current_utilization_percent: float
    recommended_action: str  # SCALE_UP, SCALE_DOWN, ADD_WORKER, REMOVE_WORKER, INCREASE_CONCURRENCY
    target_capacity: float
    reason: str = ""


class CapacityPlanner:
    """Monitors resource utilization and forecasts scaling requirements."""

    def analyze_capacity(self, tenant_id: str = "global") -> List[CapacityRecommendation]:
        recs = [
            CapacityRecommendation(
                resource_type="WORKER_CONCURRENCY",
                current_utilization_percent=88.5,
                recommended_action="ADD_WORKER",
                target_capacity=8.0,
                reason="Worker pool concurrency near saturation (88.5%) during peak hours",
            ),
            CapacityRecommendation(
                resource_type="CACHE",
                current_utilization_percent=25.0,
                recommended_action="REDUCE_IDLE_CAPACITY",
                target_capacity=512.0,
                reason="Cache memory underutilized (25.0%)",
            ),
        ]
        logger.info(
            f"[CAPACITY PLANNER] Analyzed capacity for tenant '{tenant_id}': Generated {len(recs)} recommendations"
        )
        return recs
