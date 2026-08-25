"""Service Level Objective & Indicator (SLI/SLO) Subsystem (Phase 5.31)."""

from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.reliability_platform.exceptions import SLONotFoundException, SLOBreachException
from app.platform_contracts.tenant import TenantIsolationValidator


class SLIType(str, Enum):
    AVAILABILITY = "AVAILABILITY"
    LATENCY = "LATENCY"
    ERROR_RATE = "ERROR_RATE"
    THROUGHPUT = "THROUGHPUT"
    MODEL_QUALITY = "MODEL_QUALITY"


class SLI(BaseModel):
    sli_id: str = Field(default_factory=lambda: f"sli_{uuid.uuid4().hex[:12]}")
    name: str
    sli_type: SLIType
    current_value: float  # e.g., 99.9


class SLOBudget(BaseModel):
    total_budget_pct: float = 100.0
    remaining_budget_pct: float = 100.0
    consumed_budget_pct: float = 0.0


class SLO(BaseModel):
    slo_id: str = Field(default_factory=lambda: f"slo_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    service_id: str
    name: str
    target_percentage: float = 99.9  # e.g., 99.9%
    sli: SLI
    budget: SLOBudget = Field(default_factory=SLOBudget)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class SLOBreach(BaseModel):
    breach_id: str = Field(default_factory=lambda: f"brch_{uuid.uuid4().hex[:12]}")
    slo_id: str
    tenant_id: str
    service_id: str
    remaining_budget_pct: float
    detected_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class SLOManager:
    """Manages SLIs, SLO targets, error budgets, and breach evaluation."""

    def __init__(self) -> None:
        self._slos: Dict[str, SLO] = {}

    def create_slo(
        self,
        tenant_id: str,
        service_id: str,
        name: str,
        target_percentage: float = 99.9,
        sli_type: SLIType = SLIType.AVAILABILITY,
        current_sli_value: float = 99.95,
    ) -> SLO:
        sli = SLI(name=f"{name}_SLI", sli_type=sli_type, current_value=current_sli_value)
        slo = SLO(
            tenant_id=tenant_id,
            service_id=service_id,
            name=name,
            target_percentage=target_percentage,
            sli=sli,
        )
        self._slos[slo.slo_id] = slo
        return slo

    def evaluate_slo(self, slo_id: str, tenant_id: str, observed_value: float) -> Optional[SLOBreach]:
        slo = self._slos.get(slo_id)
        if not slo:
            raise SLONotFoundException(slo_id)
        TenantIsolationValidator.validate_tenant_access(tenant_id, slo.tenant_id)

        slo.sli.current_value = observed_value
        allowed_error = 100.0 - slo.target_percentage
        observed_error = max(0.0, 100.0 - observed_value)

        if allowed_error > 0:
            consumed = min(100.0, (observed_error / allowed_error) * 100.0)
            remaining = max(0.0, 100.0 - consumed)
        else:
            remaining = 0.0 if observed_error > 0 else 100.0
            consumed = 100.0 - remaining

        slo.budget.consumed_budget_pct = round(consumed, 2)
        slo.budget.remaining_budget_pct = round(remaining, 2)

        if remaining <= 0.0:
            breach = SLOBreach(
                slo_id=slo_id,
                tenant_id=tenant_id,
                service_id=slo.service_id,
                remaining_budget_pct=remaining,
            )
            return breach
        return None
