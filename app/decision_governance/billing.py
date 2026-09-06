"""Decision cost attribution tracking reusing UnifiedCostLedger."""

from datetime import datetime, timezone
from typing import Dict, Any, Optional
from decimal import Decimal
import uuid
from pydantic import BaseModel, Field

from app.finops.cost_ledger import UnifiedCostLedger, CostCategory
from app.decision_governance.exceptions import CrossTenantDecisionGovernanceException


class DecisionCostDimension(BaseModel):
    category: str = "DECISION_REASONING"  # SIMULATION, SCENARIO_MODELING, OPTIMIZATION
    units_consumed: float = 1.0
    unit_cost_usd: float = 0.01


class DecisionCostEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    decision_id: str
    amount_usd: float = 0.0
    description: str = ""
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DecisionBillingTracker:
    """Tracks decision reasoning costs using UnifiedCostLedger."""

    def __init__(self, cost_ledger: Optional[UnifiedCostLedger] = None) -> None:
        self.cost_ledger = cost_ledger or UnifiedCostLedger()

    def record_cost(
        self,
        tenant_id: str,
        decision_id: str,
        amount_usd: float,
        description: str = "Decision reasoning computation",
    ) -> DecisionCostEvent:
        event = DecisionCostEvent(
            tenant_id=tenant_id,
            decision_id=decision_id,
            amount_usd=amount_usd,
            description=description,
        )
        self.cost_ledger.record_cost(
            component="DECISION_GOVERNANCE",
            cost_category=CostCategory.OTHER,
            quantity=Decimal("1.0"),
            unit_price=Decimal(str(amount_usd)),
            tenant_id=tenant_id,
            resource_id=decision_id,
            metadata={"description": description},
        )
        return event
