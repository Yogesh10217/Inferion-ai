"""Knowledge Billing Attribution Subsystem (Phase 5.35)."""

from typing import Dict, Any, Optional
from datetime import datetime, timezone
from decimal import Decimal
import uuid
from pydantic import BaseModel, Field

from app.finops.cost_ledger import UnifiedCostLedger, CostCategory


class KnowledgeCostEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: f"kcost_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    item_id: str
    cost_usd: float
    description: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class KnowledgeBillingTracker:
    """Attributes knowledge intelligence operational costs to UnifiedCostLedger."""

    def __init__(self, cost_ledger: Optional[UnifiedCostLedger] = None) -> None:
        self.cost_ledger = cost_ledger or UnifiedCostLedger()

    def record_knowledge_cost(
        self,
        tenant_id: str,
        item_id: str,
        cost_usd: float,
        description: str = "Knowledge Intelligence Processing",
    ) -> Dict[str, Any]:
        entry = self.cost_ledger.record_cost(
            component="knowledge_intelligence",
            cost_category=CostCategory.OTHER,
            quantity=Decimal("1.0"),
            unit_price=Decimal(str(cost_usd)),
            tenant_id=tenant_id,
            resource_id=item_id,
            metadata={"item_id": item_id, "description": description},
        )
        return entry.model_dump()
