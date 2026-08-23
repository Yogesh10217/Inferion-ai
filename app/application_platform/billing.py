"""Application Billing & FinOps Tracker (Phase 5.22 - Component 14 & Enhancement 8).

Event-driven cost attribution reusing UnifiedCostLedger (app.finops.cost_ledger):
Hierarchy:
Tenant → Organization → Workspace → Project → Application → Application Version → Execution
"""

import logging
from enum import Enum
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.finops.cost_ledger import UnifiedCostLedger, CostCategory, CostLedgerEntry

logger = logging.getLogger(__name__)


class ApplicationExecutionCostEvent(BaseModel):
    """Normalized cost event emitted during application execution."""

    event_id: str = Field(default_factory=lambda: f"cstevt_{uuid.uuid4().hex[:12]}")
    execution_id: str
    application_id: str
    application_version: str
    tenant_id: str
    organization_id: Optional[str] = None
    workspace_id: Optional[str] = None
    project_id: Optional[str] = None
    category: CostCategory = CostCategory.MODEL_INFERENCE
    amount_usd: float = 0.0
    units_consumed: float = 1.0
    resource_reference: str = ""
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ApplicationBillingTracker:
    """Attributes cost events across the application cost hierarchy to UnifiedCostLedger."""

    def __init__(self, cost_ledger: Optional[UnifiedCostLedger] = None) -> None:
        self.cost_ledger = cost_ledger or UnifiedCostLedger()
        self._events: List[ApplicationExecutionCostEvent] = []

    def record_cost_event(
        self,
        tenant_id: str,
        application_id: str,
        application_version: str,
        execution_id: str,
        category: CostCategory,
        amount_usd: float,
        organization_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        project_id: Optional[str] = None,
        units_consumed: float = 1.0,
        resource_reference: str = "",
    ) -> ApplicationExecutionCostEvent:
        evt = ApplicationExecutionCostEvent(
            execution_id=execution_id,
            application_id=application_id,
            application_version=application_version,
            tenant_id=tenant_id,
            organization_id=organization_id,
            workspace_id=workspace_id,
            project_id=project_id,
            category=category,
            amount_usd=amount_usd,
            units_consumed=units_consumed,
            resource_reference=resource_reference,
        )
        self._events.append(evt)

        # Forward directly into UnifiedCostLedger for FinOps tracking
        from decimal import Decimal
        self.cost_ledger.record_cost(
            component=f"application:{application_id}:{application_version}",
            cost_category=category,
            quantity=Decimal(str(units_consumed)),
            unit_price=Decimal(str(amount_usd)),
            tenant_id=tenant_id,
            organization_id=organization_id,
            workspace_id=workspace_id,
            project_id=project_id,
            execution_id=execution_id,
            metadata={
                "application_id": application_id,
                "application_version": application_version,
                "resource_reference": resource_reference,
            },
        )

        logger.info(f"[BILLING TRACKER] Attributed ${amount_usd:.6f} ({category.value}) to app {application_id}")
        return evt

    def get_application_total_cost(self, tenant_id: str, application_id: str) -> float:
        return sum(
            evt.amount_usd for evt in self._events
            if evt.tenant_id == tenant_id and evt.application_id == application_id
        )
