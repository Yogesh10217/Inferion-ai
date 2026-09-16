"""Reliability Financial Cost Attribution Subsystem (Phase 5.31)."""

from typing import Any, Dict, Optional

from app.finops.cost_ledger import UnifiedCostLedger


class ReliabilityBillingTracker:
    """Records cost attribution metadata for reliability incident remediations and evaluations."""

    def __init__(self, cost_ledger: Optional[UnifiedCostLedger] = None) -> None:
        self.cost_ledger = cost_ledger or UnifiedCostLedger()

    def record_reliability_cost(
        self,
        tenant_id: str,
        service_id: str,
        cost_usd: float,
        description: str,
    ) -> Dict[str, Any]:
        return self.cost_ledger.record_cost_event(
            tenant_id=tenant_id,
            cost_usd=cost_usd,
            category="RELIABILITY_OPERATIONS",
            metadata={"service_id": service_id, "description": description},
        )
