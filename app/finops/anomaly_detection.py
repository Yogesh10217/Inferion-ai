"""Cost Anomaly & Runaway Execution Detection Subsystem."""

import logging
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from typing import Any, List, Optional

from pydantic import BaseModel, Field, field_validator

from app.observability.anomaly_detection import AnomalyDetector as BaseAnomalyDetector

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class AnomalyType(str, Enum):
    COST_SPIKE = "COST_SPIKE"
    TOKEN_SPIKE = "TOKEN_SPIKE"
    REQUEST_SPIKE = "REQUEST_SPIKE"
    RUNAWAY_AGENT = "RUNAWAY_AGENT"
    RUNAWAY_WORKFLOW = "RUNAWAY_WORKFLOW"
    RETRY_STORM = "RETRY_STORM"
    IDLE_RESOURCE_COST = "IDLE_RESOURCE_COST"


class CostAnomalySeverity(str, Enum):
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class CostAnomaly(BaseModel):
    anomaly_id: str = Field(default_factory=lambda: f"anom_{uuid.uuid4().hex[:10]}")
    tenant_id: str = "global"
    anomaly_type: AnomalyType = AnomalyType.COST_SPIKE
    severity: CostAnomalySeverity = CostAnomalySeverity.HIGH

    observed_value: Decimal = Decimal("0.0")
    baseline_value: Decimal = Decimal("0.0")
    deviation_percent: float = 0.0

    resource_id: Optional[str] = None
    recommended_action: str = "THROTTLE_EXECUTION"
    detected_at: datetime = Field(default_factory=_now)

    @field_validator("observed_value", "baseline_value", mode="before")
    @classmethod
    def parse_decimal(cls, value: Any) -> Decimal:
        if isinstance(value, float):
            return Decimal(str(value))
        return Decimal(value)


class CostAnomalyDetector:
    """Detects cost spikes, runaway agents, retry storms, and idle resource waste."""

    def __init__(self, base_detector: Optional[BaseAnomalyDetector] = None) -> None:
        self.base_detector = base_detector or BaseAnomalyDetector()
        self._anomalies: List[CostAnomaly] = []

    def detect_runaway_execution(
        self,
        tenant_id: str,
        execution_id: str,
        observed_cost: Decimal,
        baseline_cost: Decimal,
        threshold_multiplier: float = 3.0,
    ) -> Optional[CostAnomaly]:
        obs_dec = Decimal(str(observed_cost)) if isinstance(observed_cost, (float, int, str)) else observed_cost
        base_dec = Decimal(str(baseline_cost)) if isinstance(baseline_cost, (float, int, str)) else baseline_cost

        if base_dec > Decimal("0.0") and (obs_dec / base_dec) >= Decimal(str(threshold_multiplier)):
            dev_pct = float((obs_dec - base_dec) / base_dec * Decimal("100.0"))
            anom = CostAnomaly(
                tenant_id=tenant_id,
                anomaly_type=AnomalyType.RUNAWAY_AGENT,
                severity=CostAnomalySeverity.CRITICAL if dev_pct >= 200.0 else CostAnomalySeverity.HIGH,
                observed_value=obs_dec,
                baseline_value=base_dec,
                deviation_percent=dev_pct,
                resource_id=execution_id,
                recommended_action="PAUSE_AGENT_EXECUTION",
            )
            self._anomalies.append(anom)
            logger.warning(
                f"[COST ANOMALY] Runaway execution detected on tenant '{tenant_id}' (Observed: ${obs_dec}, Baseline: ${base_dec}) -> CRITICAL"
            )
            return anom

        return None

    def list_anomalies(self, tenant_id: Optional[str] = None) -> List[CostAnomaly]:
        res = self._anomalies
        if tenant_id:
            res = [a for a in res if a.tenant_id == tenant_id]
        return res
