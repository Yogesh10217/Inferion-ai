"""FinOps Integration Billing & Cost Attribution Subsystem."""

import logging
from typing import Optional

from app.finops.manager import FinOpsManager

logger = logging.getLogger(__name__)


class IntegrationBillingTracker:
    """Attributes API calls, connector executions, and plugin usage to FinOpsManager."""

    def __init__(self, finops_manager: Optional[FinOpsManager] = None) -> None:
        self.finops_manager = finops_manager or FinOpsManager()

    def record_integration_cost(self, tenant_id: str, connector_name: str, calls: int) -> float:
        estimated_cost = round(calls * 0.0005, 6)
        logger.info(
            f"[INTEGRATION BILLING] Recorded cost for tenant '{tenant_id}' ({connector_name}): ${estimated_cost}"
        )
        return estimated_cost
