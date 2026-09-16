"""Event Cost Attribution Subsystem (Phase 5.34)."""

from decimal import Decimal
from typing import Any, Dict, Optional

from app.finops.cost_ledger import CostCategory, UnifiedCostLedger


class EventBillingTracker:
    """Records cost attribution metadata for event processing, correlation, automation, and investigation."""

    def __init__(self, cost_ledger: Optional[UnifiedCostLedger] = None) -> None:
        self.cost_ledger = cost_ledger or UnifiedCostLedger()

    def record_event_cost(
        self,
        tenant_id: str,
        event_id: str,
        cost_usd: float,
        description: str,
    ) -> Dict[str, Any]:
        entry = self.cost_ledger.record_cost(
            component="event_intelligence",
            cost_category=CostCategory.OTHER,
            quantity=Decimal("1.0"),
            unit_price=Decimal(str(cost_usd)),
            tenant_id=tenant_id,
            resource_id=event_id,
            metadata={"event_id": event_id, "description": description},
        )
        return entry.model_dump()
