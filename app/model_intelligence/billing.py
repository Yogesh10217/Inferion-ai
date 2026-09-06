"""FinOps & Cost Attribution for Model Intelligence (Phase 5.44)."""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from decimal import Decimal
from app.finops.cost_ledger import UnifiedCostLedger, CostCategory as PlatformCostCategory
from app.finops.manager import FinOpsManager
from app.model_intelligence.exceptions import CrossTenantModelIntelligenceException

logger = logging.getLogger(__name__)


class ModelIntelligenceCostEvent(BaseModel):
    event_id: str
    model_id: str
    tenant_id: str
    operation: str  # evaluation, benchmarking, monitoring, assurance_check
    cost_usd: float
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ModelIntelligenceBillingTracker:
    """Tracks intelligence operation costs using UnifiedCostLedger and FinOpsManager without duplicating cost accounting."""

    def __init__(self) -> None:
        self.cost_ledger = UnifiedCostLedger()
        self.finops_manager = FinOpsManager()
        self._cost_events: Dict[str, List[ModelIntelligenceCostEvent]] = {}

    def track_operation_cost(
        self,
        model_id: str,
        tenant_id: str,
        operation: str,
        cost_usd: float,
    ) -> ModelIntelligenceCostEvent:
        e_id = f"mcost-{uuid.uuid4().hex[:8]}"

        event = ModelIntelligenceCostEvent(
            event_id=e_id,
            model_id=model_id,
            tenant_id=tenant_id,
            operation=operation,
            cost_usd=cost_usd,
        )

        if model_id not in self._cost_events:
            self._cost_events[model_id] = []
        self._cost_events[model_id].append(event)

        # Record into UnifiedCostLedger
        self.cost_ledger.record_cost(
            component=f"model_intelligence.{operation.lower()}",
            cost_category=PlatformCostCategory.COMPUTE,
            quantity=Decimal("1.0"),
            unit_price=Decimal(str(cost_usd)),
            tenant_id=tenant_id,
            metadata={"model_id": model_id, "cost_event_id": e_id},
        )

        logger.info(f"[MODEL BILLING] Recorded intelligence cost ${cost_usd:.4f} for model {model_id} (Operation: {operation})")
        return event

    def get_total_cost(self, model_id: str, tenant_id: str) -> float:
        events = self._cost_events.get(model_id, [])
        for e in events:
            if e.tenant_id != tenant_id:
                raise CrossTenantModelIntelligenceException()
        return sum(e.cost_usd for e in events)
