"""SLO & Error Budget Management Subsystem."""

from datetime import datetime, timezone
from enum import Enum
import uuid
import logging
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field

from app.observability.sla import SLAEngine as BaseSLAEngine


logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class SLOType(str, Enum):
    AVAILABILITY = "AVAILABILITY"
    LATENCY = "LATENCY"
    ERROR_RATE = "ERROR_RATE"
    THROUGHPUT = "THROUGHPUT"
    QUEUE_DELAY = "QUEUE_DELAY"
    MODEL_LATENCY = "MODEL_LATENCY"
    TOKEN_LATENCY = "TOKEN_LATENCY"
    TOOL_SUCCESS_RATE = "TOOL_SUCCESS_RATE"
    WORKFLOW_SUCCESS_RATE = "WORKFLOW_SUCCESS_RATE"
    DATA_FRESHNESS = "DATA_FRESHNESS"
    QUALITY_SCORE = "QUALITY_SCORE"
    CUSTOM = "CUSTOM"


class SLOStatus(str, Enum):
    HEALTHY = "HEALTHY"
    WARNING = "WARNING"
    BREACHED = "BREACHED"


class ServiceLevelObjective(BaseModel):
    slo_id: str = Field(default_factory=lambda: f"slo_{uuid.uuid4().hex[:10]}")
    name: str
    tenant_id: str = "global"
    slo_type: SLOType = SLOType.AVAILABILITY
    target_percentage: float = 99.9

    current_value: float = 100.0
    error_budget_remaining_percent: float = 100.0
    burn_rate: float = 0.0
    status: SLOStatus = SLOStatus.HEALTHY

    window_days: int = 30
    created_at: datetime = Field(default_factory=_now)


class SLOManager:
    """Evaluates Service Level Objectives, error budgets, and burn-rates per tenant."""

    def __init__(self, base_sla_engine: Optional[BaseSLAEngine] = None) -> None:
        self.base_sla_engine = base_sla_engine or BaseSLAEngine()
        self._slos: Dict[str, ServiceLevelObjective] = {}


    def create_slo(
        self,
        name: str,
        target_percentage: float,
        tenant_id: str = "global",
        slo_type: SLOType = SLOType.AVAILABILITY,
        window_days: int = 30,
    ) -> ServiceLevelObjective:
        slo = ServiceLevelObjective(
            name=name,
            target_percentage=target_percentage,
            tenant_id=tenant_id,
            slo_type=slo_type,
            window_days=window_days,
        )
        self._slos[slo.slo_id] = slo
        logger.info(f"[SLO MANAGER] Created SLO '{name}' (Target: {target_percentage}%, Tenant: '{tenant_id}')")
        return slo

    def record_measurement(self, slo_id: str, current_value: float) -> ServiceLevelObjective:
        slo = self.get_slo(slo_id)
        slo.current_value = current_value

        allowed_error = 100.0 - slo.target_percentage
        actual_error = max(0.0, 100.0 - current_value)

        if current_value >= slo.target_percentage:
            remaining_eb = 100.0
            burn = 0.0
        else:
            remaining_eb = max(0.0, 100.0 - (actual_error / allowed_error * 100.0)) if allowed_error > 0.0 else 0.0
            burn = float(actual_error / allowed_error) if allowed_error > 0.0 else 1.0

        slo.error_budget_remaining_percent = float(remaining_eb)
        slo.burn_rate = burn

        if current_value < slo.target_percentage:
            slo.status = SLOStatus.BREACHED
        elif remaining_eb <= 20.0:
            slo.status = SLOStatus.WARNING
        else:
            slo.status = SLOStatus.HEALTHY

        logger.info(f"[SLO MANAGER] Measured SLO '{slo.name}': Current = {current_value}%, Error Budget = {remaining_eb:.1f}%, Status = {slo.status.value}")
        return slo


    def get_slo(self, slo_id: str) -> ServiceLevelObjective:
        slo = self._slos.get(slo_id)
        if not slo:
            raise KeyError(f"SLO '{slo_id}' not found")
        return slo

    def list_slos(self, tenant_id: Optional[str] = None) -> List[ServiceLevelObjective]:
        res = list(self._slos.values())
        if tenant_id:
            res = [s for s in res if s.tenant_id == tenant_id]
        return res
