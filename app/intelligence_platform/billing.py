"""Financial Cost Attribution wrapping UnifiedCostLedger."""

import logging
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import Dict, Optional

from pydantic import BaseModel, Field

from app.finops.cost_ledger import CostCategory, UnifiedCostLedger

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class IntelligenceCostEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: f"cost_{uuid.uuid4().hex[:10]}")
    tenant_id: str = "global"
    operation_type: str  # CONTEXT_RETRIEVAL, FORECASTING, SIMULATION, OPTIMIZATION, RECOMMENDATION, EXECUTION
    amount_usd: float = 0.005
    resource_id: Optional[str] = None
    recorded_at: datetime = Field(default_factory=_now)


class IntelligenceBillingTracker:
    """Attributes cost events to UnifiedCostLedger."""

    def __init__(self, cost_ledger: Optional[UnifiedCostLedger] = None) -> None:
        self.cost_ledger = cost_ledger or UnifiedCostLedger()
        self._events: Dict[str, IntelligenceCostEvent] = {}

    def record_operation_cost(
        self,
        tenant_id: str,
        operation_type: str,
        amount_usd: float = 0.005,
        resource_id: Optional[str] = None,
    ) -> IntelligenceCostEvent:
        evt = IntelligenceCostEvent(
            tenant_id=tenant_id,
            operation_type=operation_type,
            amount_usd=amount_usd,
            resource_id=resource_id,
        )

        try:
            self.cost_ledger.record_cost(
                component="INTELLIGENCE_PLATFORM",
                cost_category=CostCategory.OTHER,
                quantity=Decimal("1.0"),
                unit_price=Decimal(str(amount_usd)),
                tenant_id=tenant_id,
                resource_id=resource_id or "global",
            )
        except Exception as e:
            logger.debug(f"UnifiedCostLedger recording note: {e}")

        self._events[evt.event_id] = evt
        logger.info(
            f"[INTELLIGENCE BILLING] Recorded ${amount_usd:.4f} for operation {operation_type} on tenant '{tenant_id}'"
        )
        return evt
