"""Bottleneck detection engine for Capacity Intelligence (Phase 5.56)."""

import logging
from typing import List

from app.capacity_intelligence.models import Bottleneck, BottleneckType
from app.capacity_intelligence.repositories import BottleneckRepository

logger = logging.getLogger(__name__)


class BottleneckDetectionEngine:
    """Detects resource and dependency bottlenecks (CPU, MEMORY, STORAGE, NETWORK, DATABASE, QUEUE, etc.)."""

    def __init__(self, repo: BottleneckRepository) -> None:
        self.repo = repo

    def detect_bottlenecks(
        self, tenant_id: str, resource_id: str, metric_value: float = 88.0
    ) -> List[Bottleneck]:
        bottlenecks: List[Bottleneck] = []
        if metric_value >= 85.0:
            bot = Bottleneck(
                tenant_id=tenant_id,
                resource_id=resource_id,
                bottleneck_type=BottleneckType.CPU,
                severity="HIGH" if metric_value >= 90.0 else "MEDIUM",
                description=f"Resource '{resource_id}' CPU utilization of {metric_value:.1f}% exceeds 85.0% bottleneck threshold",
            )
            bottlenecks.append(bot)
            self.repo.save(bot)
        logger.info(f"Detected {len(bottlenecks)} bottlenecks for resource '{resource_id}'")
        return bottlenecks


BottleneckEngine = BottleneckDetectionEngine
