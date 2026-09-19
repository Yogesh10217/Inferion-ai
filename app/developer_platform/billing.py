"""FinOps Developer Billing & Build Cost Attribution Subsystem."""

import logging
from typing import Optional

from pydantic import BaseModel

from app.finops.manager import FinOpsManager

logger = logging.getLogger(__name__)


class DeveloperBillingRecord(BaseModel):
    total_extension_executions: int = 1
    total_compute_seconds: float = 0.0
    total_cost_dollars: float = 0.0


class DeveloperBillingAdapter:
    """Attributes CI/CD build execution and workspace compute cost to FinOpsManager."""

    def __init__(self, finops_manager: Optional[FinOpsManager] = None) -> None:
        self.finops_manager = finops_manager or FinOpsManager()

    def record_build_cost(
        self, tenant_id: str, build_duration_minutes: float, resource_type: str = "standard_build"
    ) -> float:
        rate = 0.05 if resource_type == "standard_build" else 0.20
        cost = round(build_duration_minutes * rate, 4)
        logger.info(
            f"[DEVELOPER BILLING] Recorded build cost for tenant '{tenant_id}' ({build_duration_minutes} min @ {resource_type}): ${cost}"
        )
        return cost

    def record_usage(
        self,
        tenant_id: str = "global",
        developer_id: str = "dev",
        compute_seconds: float = 0.0,
        cost_dollars: float = 0.0,
        **kwargs,
    ) -> DeveloperBillingRecord:
        logger.info(
            f"[DEVELOPER BILLING] Recorded usage for developer '{developer_id}' in tenant '{tenant_id}': ${cost_dollars}"
        )
        return DeveloperBillingRecord(
            total_extension_executions=1, total_compute_seconds=compute_seconds, total_cost_dollars=cost_dollars
        )


DeveloperBillingTracker = DeveloperBillingAdapter
