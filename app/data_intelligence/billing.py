"""Data intelligence cost attribution (Phase 5.43)."""

import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from decimal import Decimal
from pydantic import BaseModel, Field

from app.finops.cost_ledger import UnifiedCostLedger, CostCategory as PlatformCostCategory


class DataIntelligenceCostEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: f"ev-data-cost-{uuid.uuid4().hex[:12]}")
    tenant_id: str
    dataset_id: str
    operation: str  # PROFILING, QUALITY_EVAL, DRIFT_EVAL
    amount_usd: float
    recorded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DataIntelligenceBillingTracker:
    """Delegates cost recording to UnifiedCostLedger without duplicating cost entries."""

    def __init__(self) -> None:
        self.cost_ledger = UnifiedCostLedger()
        self._events: List[DataIntelligenceCostEvent] = []

    def record_cost_event(
        self,
        tenant_id: str,
        dataset_id: str,
        operation: str,
        amount_usd: float,
        cost_category: PlatformCostCategory = PlatformCostCategory.COMPUTE,
    ) -> DataIntelligenceCostEvent:
        event = DataIntelligenceCostEvent(
            tenant_id=tenant_id,
            dataset_id=dataset_id,
            operation=operation,
            amount_usd=amount_usd,
        )
        self._events.append(event)

        # Delegate cost recording to UnifiedCostLedger
        self.cost_ledger.record_cost(
            component=f"data_intelligence.{operation.lower()}",
            cost_category=cost_category,
            quantity=Decimal("1.0"),
            unit_price=Decimal(str(amount_usd)),
            tenant_id=tenant_id,
            metadata={"dataset_id": dataset_id, "data_event_id": event.event_id},
        )
        return event

    def get_tenant_total_spend(self, tenant_id: str) -> float:
        return sum(e.amount_usd for e in self._events if e.tenant_id == tenant_id)
