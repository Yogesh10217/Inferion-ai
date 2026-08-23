"""Capacity Forecasting & Resource Allocation Management Engine."""

from datetime import datetime, timezone
from enum import Enum
import uuid
import logging
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field

from app.finops.cost_ledger import UnifiedCostLedger

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class CapacityRisk(str, Enum):
    NONE = "NONE"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class CapacityAssessment(BaseModel):
    assessment_id: str = Field(default_factory=lambda: f"cap_{uuid.uuid4().hex[:10]}")
    tenant_id: str = "global"
    service_id: str
    cpu_utilization_pct: float = 50.0
    memory_utilization_pct: float = 50.0
    queue_backlog_count: int = 0
    error_budget_burn_rate: float = 1.0
    risk: CapacityRisk = CapacityRisk.LOW
    recommendation: str = "MAINTAIN"  # MAINTAIN, SCALE_UP, SCALE_DOWN, THROTTLE, REROUTE
    estimated_cost_impact_usd: float = 0.0
    assessed_at: datetime = Field(default_factory=_now)


class CapacityManager:
    """Monitors capacity metrics, queue growth, backlog, and consults FinOps before scaling."""

    def __init__(self, cost_ledger: Optional[UnifiedCostLedger] = None) -> None:
        self.cost_ledger = cost_ledger or UnifiedCostLedger()
        self._assessments: Dict[str, CapacityAssessment] = {}

    def assess_service_capacity(
        self,
        tenant_id: str,
        service_id: str,
        cpu_utilization_pct: float = 50.0,
        memory_utilization_pct: float = 50.0,
        queue_backlog_count: int = 0,
        error_budget_burn_rate: float = 1.0,
    ) -> CapacityAssessment:
        # Determine risk level
        if cpu_utilization_pct > 90.0 or queue_backlog_count > 500 or error_budget_burn_rate > 5.0:
            risk = CapacityRisk.CRITICAL
            recommendation = "SCALE_UP"
            cost_impact = 50.0
        elif cpu_utilization_pct > 75.0 or queue_backlog_count > 100 or error_budget_burn_rate > 2.0:
            risk = CapacityRisk.HIGH
            recommendation = "SCALE_UP"
            cost_impact = 20.0
        elif cpu_utilization_pct < 15.0 and memory_utilization_pct < 20.0 and queue_backlog_count == 0:
            risk = CapacityRisk.NONE
            recommendation = "SCALE_DOWN"
            cost_impact = -15.0
        else:
            risk = CapacityRisk.LOW
            recommendation = "MAINTAIN"
            cost_impact = 0.0

        assessment = CapacityAssessment(
            tenant_id=tenant_id,
            service_id=service_id,
            cpu_utilization_pct=cpu_utilization_pct,
            memory_utilization_pct=memory_utilization_pct,
            queue_backlog_count=queue_backlog_count,
            error_budget_burn_rate=error_budget_burn_rate,
            risk=risk,
            recommendation=recommendation,
            estimated_cost_impact_usd=cost_impact,
        )
        self._assessments[service_id] = assessment
        logger.info(f"[CAPACITY MANAGER] Capacity for service '{service_id}': Risk={risk.value}, Recommendation={recommendation}")
        return assessment

    def get_latest_assessment(self, service_id: str, tenant_id: str) -> CapacityAssessment:
        if service_id not in self._assessments:
            # Generate default on demand
            return self.assess_service_capacity(tenant_id=tenant_id, service_id=service_id)
        ass = self._assessments[service_id]
        if ass.tenant_id not in (tenant_id, "global"):
            raise ValueError(f"Capacity assessment for service '{service_id}' not accessible by tenant '{tenant_id}'.")
        return ass
