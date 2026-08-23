"""Service Level Objective (SLO) & Error Budget Tracking Manager."""

from datetime import datetime, timezone
from enum import Enum
import uuid
import logging
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class SLOType(str, Enum):
    AVAILABILITY = "AVAILABILITY"
    LATENCY = "LATENCY"
    ERROR_RATE = "ERROR_RATE"
    THROUGHPUT = "THROUGHPUT"
    QUALITY_DEGRADATION = "QUALITY_DEGRADATION"
    SAFETY_VIOLATION = "SAFETY_VIOLATION"


class SLOStatus(str, Enum):
    HEALTHY = "HEALTHY"
    WARNING = "WARNING"
    BREACHED = "BREACHED"


class ServiceLevelIndicator(BaseModel):
    sli_id: str = Field(default_factory=lambda: f"sli_{uuid.uuid4().hex[:8]}")
    name: str
    current_value: float
    unit: str = "percentage"
    timestamp: datetime = Field(default_factory=_now)


class ErrorBudget(BaseModel):
    total_budget: float = 100.0  # e.g., 0.1% allowable failure for 99.9% target
    remaining_budget: float = 100.0
    consumed_percentage: float = 0.0
    burn_rate: float = 0.0  # 1.0 = normal burn, >1.0 = accelerated burn
    status: SLOStatus = SLOStatus.HEALTHY


class ServiceLevelObjective(BaseModel):
    slo_id: str = Field(default_factory=lambda: f"slo_{uuid.uuid4().hex[:10]}")
    tenant_id: str = "global"
    service_id: str
    name: str
    description: str = ""
    slo_type: SLOType = SLOType.AVAILABILITY
    target_threshold: float = 99.9  # Target e.g. 99.9%
    time_window_days: int = 30
    current_indicator: ServiceLevelIndicator
    error_budget: ErrorBudget = Field(default_factory=ErrorBudget)
    status: SLOStatus = SLOStatus.HEALTHY
    created_at: datetime = Field(default_factory=_now)
    updated_at: datetime = Field(default_factory=_now)


class SLOManager:
    """Manages multi-tenant Service Level Objectives and Error Budget burn rate tracking."""

    def __init__(self) -> None:
        self._slos: Dict[str, ServiceLevelObjective] = {}

    def create_slo(
        self,
        tenant_id: str,
        service_id: str,
        name: str,
        slo_type: SLOType,
        target_threshold: float = 99.9,
        description: str = "",
        initial_value: float = 99.95,
    ) -> ServiceLevelObjective:
        sli = ServiceLevelIndicator(name=f"{name}_sli", current_value=initial_value)
        total_allowable_error = max(0.001, round(100.0 - target_threshold, 4))
        current_error = max(0.0, round(100.0 - initial_value, 4))

        consumed_pct = round(min(100.0, (current_error / total_allowable_error) * 100.0), 2)
        rem_budget = round(max(0.0, 100.0 - consumed_pct), 2)

        eb = ErrorBudget(
            total_budget=total_allowable_error,
            remaining_budget=rem_budget,
            consumed_percentage=consumed_pct,
            burn_rate=1.0 if consumed_pct < 50 else 2.5,
            status=SLOStatus.HEALTHY if rem_budget > 20 else (SLOStatus.WARNING if rem_budget > 0 else SLOStatus.BREACHED),
        )

        slo = ServiceLevelObjective(
            tenant_id=tenant_id,
            service_id=service_id,
            name=name,
            slo_type=slo_type,
            target_threshold=target_threshold,
            description=description,
            current_indicator=sli,
            error_budget=eb,
            status=eb.status,
        )
        self._slos[slo.slo_id] = slo
        logger.info(f"[SLO MANAGER] Created SLO '{name}' ({slo.slo_id}) for service {service_id} (Target: {target_threshold}%)")
        return slo

    def update_slo_indicator(
        self,
        slo_id: str,
        tenant_id: str,
        current_value: float,
    ) -> ServiceLevelObjective:
        if slo_id not in self._slos:
            raise ValueError(f"SLO '{slo_id}' not found.")

        slo = self._slos[slo_id]
        if slo.tenant_id not in (tenant_id, "global"):
            raise ValueError(f"SLO '{slo_id}' not accessible by tenant '{tenant_id}'.")

        slo.current_indicator.current_value = current_value
        slo.current_indicator.timestamp = _now()

        total_allowable_error = max(0.001, round(100.0 - slo.target_threshold, 4))
        current_error = max(0.0, round(100.0 - current_value, 4))

        consumed_pct = round(min(100.0, (current_error / total_allowable_error) * 100.0), 2)
        rem_budget = round(max(0.0, 100.0 - consumed_pct), 2)

        status = SLOStatus.HEALTHY if rem_budget > 20 else (SLOStatus.WARNING if rem_budget > 0 else SLOStatus.BREACHED)
        burn_rate = round(consumed_pct / 50.0, 2) if consumed_pct > 0 else 0.5

        slo.error_budget = ErrorBudget(
            total_budget=total_allowable_error,
            remaining_budget=rem_budget,
            consumed_percentage=consumed_pct,
            burn_rate=burn_rate,
            status=status,
        )
        slo.status = status
        slo.updated_at = _now()
        logger.info(f"[SLO MANAGER] Updated SLO '{slo.name}' value to {current_value} (Status: {status.value})")
        return slo

    def get_slo(self, slo_id: str, tenant_id: str) -> ServiceLevelObjective:
        if slo_id not in self._slos:
            raise ValueError(f"SLO '{slo_id}' not found.")
        slo = self._slos[slo_id]
        if slo.tenant_id not in (tenant_id, "global"):
            raise ValueError(f"SLO '{slo_id}' not accessible by tenant '{tenant_id}'.")
        return slo

    def list_slos(self, tenant_id: str, service_id: Optional[str] = None) -> List[ServiceLevelObjective]:
        results = [s for s in self._slos.values() if s.tenant_id in (tenant_id, "global")]
        if service_id:
            results = [s for s in results if s.service_id == service_id]
        return results
