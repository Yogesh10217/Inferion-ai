"""Operational SLA/SLO Intelligence (Phase 5.41)."""

from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.operations_intelligence.exceptions import CrossTenantOperationsAccessException


class SLOBreachRisk(str, Enum):
    CRITICAL_BREACH = "CRITICAL_BREACH"
    BREACH_WARNING = "BREACH_WARNING"
    STABLE = "STABLE"


class ServiceObjective(BaseModel):
    slo_id: str = Field(default_factory=lambda: f"slo_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    service_id: str
    target_availability_pct: float = 99.9
    target_p99_latency_ms: float = 500.0


class SLAAssessment(BaseModel):
    assessment_id: str = Field(default_factory=lambda: f"sla_asm_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    service_id: str
    observed_availability_pct: float = 99.95
    observed_p99_latency_ms: float = 250.0
    breach_risk: SLOBreachRisk = SLOBreachRisk.STABLE
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ServiceObjectiveManager:
    """Manages operational service level objectives (SLOs) and SLA breach risk detection."""

    def __init__(self) -> None:
        self._slos: Dict[str, ServiceObjective] = {}

    def register_slo(
        self,
        tenant_id: str,
        service_id: str,
        target_availability_pct: float = 99.9,
        target_p99_latency_ms: float = 500.0,
    ) -> ServiceObjective:
        slo = ServiceObjective(
            tenant_id=tenant_id,
            service_id=service_id,
            target_availability_pct=target_availability_pct,
            target_p99_latency_ms=target_p99_latency_ms,
        )
        self._slos[slo.slo_id] = slo
        return slo

    def evaluate_sla(
        self,
        tenant_id: str,
        service_id: str,
        observed_availability_pct: float,
        observed_p99_latency_ms: float,
    ) -> SLAAssessment:
        slos = [s for s in self._slos.values() if s.tenant_id == tenant_id and s.service_id == service_id]
        target_avail = slos[0].target_availability_pct if slos else 99.9
        target_lat = slos[0].target_p99_latency_ms if slos else 500.0

        if observed_availability_pct < target_avail or observed_p99_latency_ms > target_lat:
            risk = SLOBreachRisk.CRITICAL_BREACH
        elif observed_availability_pct < target_avail + 0.05 or observed_p99_latency_ms > target_lat * 0.8:
            risk = SLOBreachRisk.BREACH_WARNING
        else:
            risk = SLOBreachRisk.STABLE

        return SLAAssessment(
            tenant_id=tenant_id,
            service_id=service_id,
            observed_availability_pct=observed_availability_pct,
            observed_p99_latency_ms=observed_p99_latency_ms,
            breach_risk=risk,
        )

    def get_slo(self, tenant_id: str, slo_id: str) -> ServiceObjective:
        slo = self._slos.get(slo_id)
        if not slo or slo.tenant_id != tenant_id:
            raise CrossTenantOperationsAccessException()
        return slo
