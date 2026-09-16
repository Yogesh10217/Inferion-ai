"""Knowledge Assurance Billing Module.

Attributes knowledge assurance computation costs using UnifiedCostLedger without duplicating financial entries.
"""

import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field

from app.finops.cost_ledger import CostCategory, UnifiedCostLedger


class KnowledgeCostDimension(BaseModel):
    category: str = "CONTEXT_ASSEMBLY"  # CONTEXT_ASSEMBLY, CONFLICT_DETECTION, ASSURANCE_EVALUATION, GRAPH_TRAVERSAL
    units_consumed: float = 1.0
    unit_cost_usd: float = 0.005


class KnowledgeCostEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: f"kcost-{uuid.uuid4().hex[:8]}")
    tenant_id: str
    resource_id: str
    amount_usd: float = 0.0
    description: str = ""
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class KnowledgeBillingTracker:
    """Tracks knowledge intelligence, context assembly, and assurance computation costs."""

    def __init__(self, cost_ledger: Optional[UnifiedCostLedger] = None) -> None:
        self.cost_ledger = cost_ledger or UnifiedCostLedger()

    def record_cost(
        self,
        tenant_id: str,
        resource_id: str,
        amount_usd: float,
        description: str = "Knowledge assurance computation",
    ) -> KnowledgeCostEvent:
        event = KnowledgeCostEvent(
            tenant_id=tenant_id,
            resource_id=resource_id,
            amount_usd=amount_usd,
            description=description,
        )
        self.cost_ledger.record_cost(
            component="KNOWLEDGE_ASSURANCE",
            cost_category=CostCategory.OTHER,
            quantity=Decimal("1.0"),
            unit_price=Decimal(str(amount_usd)),
            tenant_id=tenant_id,
            resource_id=resource_id,
            metadata={"description": description},
        )
        return event
