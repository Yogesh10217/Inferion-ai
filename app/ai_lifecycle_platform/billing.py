"""Lifecycle Cost Attribution Subsystem (Phase 5.33)."""

from typing import Any, Dict, Optional

from app.finops.cost_ledger import UnifiedCostLedger


class LifecycleBillingTracker:
    """Records cost attribution metadata for evaluation runs, artifact processing, and lifecycle governance."""

    def __init__(self, cost_ledger: Optional[UnifiedCostLedger] = None) -> None:
        self.cost_ledger = cost_ledger or UnifiedCostLedger()

    def record_lifecycle_cost(
        self,
        tenant_id: str,
        asset_id: str,
        cost_usd: float,
        description: str,
    ) -> Dict[str, Any]:
        return self.cost_ledger.record_cost_event(
            tenant_id=tenant_id,
            cost_usd=cost_usd,
            category="AI_LIFECYCLE_OPERATIONS",
            metadata={"asset_id": asset_id, "description": description},
        )
