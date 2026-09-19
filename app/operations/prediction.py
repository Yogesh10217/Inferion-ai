"""Failure Prediction & Early-Warning Operational Risk Forecast Subsystem."""

import logging
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class PredictionRiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class FailurePrediction(BaseModel):
    prediction_id: str = Field(default_factory=lambda: f"pred_{uuid.uuid4().hex[:10]}")
    resource_id: str
    tenant_id: str = "global"

    risk_level: PredictionRiskLevel = PredictionRiskLevel.MEDIUM
    confidence_score: float = Field(default=0.88, ge=0.0, le=1.0)
    predictive_signal: str  # ERROR_BURST, QUEUE_GROWTH, WORKER_SATURATION, MEMORY_TREND, CONNECTION_DEPLETION, PROVIDER_DEGRADATION, RETRY_STORM
    recommended_action: str = ""
    predicted_at: datetime = Field(default_factory=_now)


class FailurePredictionEngine:
    """Monitors early warning signals (queue depth, memory trend, retry storms) to forecast operational failures."""

    def predict_capacity_risk(
        self,
        tenant_id: str,
        resource_id: str,
        current_queue_depth: int,
        max_capacity: int = 100,
    ) -> Optional[FailurePrediction]:
        utilization = float(current_queue_depth) / float(max_capacity) * 100.0

        if utilization >= 85.0:
            pred = FailurePrediction(
                resource_id=resource_id,
                tenant_id=tenant_id,
                risk_level=PredictionRiskLevel.CRITICAL if utilization >= 95.0 else PredictionRiskLevel.HIGH,
                confidence_score=0.92,
                predictive_signal="QUEUE_GROWTH",
                recommended_action="SCALE_WORKER_POOL",
            )
            logger.warning(
                f"[FAILURE PREDICTION] High capacity risk predicted for '{resource_id}' (Utilization: {utilization:.1f}%) -> {pred.risk_level.value}"
            )
            return pred

        return None
