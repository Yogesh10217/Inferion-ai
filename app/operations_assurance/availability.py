"""Availability intelligence evaluating service availability, dependency availability, SLO performance, and SLA compliance."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, Optional

from pydantic import BaseModel, Field


class SloStatus(str, Enum):
    MET = "MET"
    AT_RISK = "AT_RISK"
    BREACHED = "BREACHED"


class AvailabilityReport(BaseModel):
    report_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    service_id: str
    uptime_percentage: float = 99.9
    slo_target: float = 99.9
    slo_status: SloStatus = SloStatus.MET
    error_budget_remaining_percentage: float = 100.0
    dependency_availability_score: float = 99.5
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class OperationsAvailabilityEngine:
    """Evaluates service availability against defined SLOs and SLAs."""

    def __init__(self) -> None:
        self._reports: Dict[str, Dict[str, AvailabilityReport]] = {}  # tenant_id -> {service_id: report}

    def evaluate_availability(
        self,
        tenant_id: str,
        service_id: str,
        uptime_percentage: float = 99.9,
        slo_target: float = 99.9,
        dependency_availability: float = 99.5,
    ) -> AvailabilityReport:
        error_budget = 100.0 - slo_target
        actual_downtime = max(0.0, 100.0 - uptime_percentage)
        budget_remaining = max(0.0, 100.0 * (1.0 - (actual_downtime / (error_budget + 1e-6))))

        if uptime_percentage >= slo_target:
            status = SloStatus.MET
        elif budget_remaining > 20.0:
            status = SloStatus.AT_RISK
        else:
            status = SloStatus.BREACHED

        report = AvailabilityReport(
            tenant_id=tenant_id,
            service_id=service_id,
            uptime_percentage=uptime_percentage,
            slo_target=slo_target,
            slo_status=status,
            error_budget_remaining_percentage=round(budget_remaining, 2),
            dependency_availability_score=dependency_availability,
        )

        if tenant_id not in self._reports:
            self._reports[tenant_id] = {}
        self._reports[tenant_id][service_id] = report
        return report

    def get_report(self, tenant_id: str, service_id: str) -> Optional[AvailabilityReport]:
        return self._reports.get(tenant_id, {}).get(service_id)
