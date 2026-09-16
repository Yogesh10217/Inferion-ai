"""Resilience Cost Attribution Subsystem (Phase 5.37)."""

import uuid
from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, Field

from app.finops.manager import FinOpsManager
from app.platform_contracts.tenant import TenantAccessGuard


class ResilienceCostEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: f"rescost_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    resource_id: str
    operation_type: str
    cost_dollars: float = 0.0
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ResilienceBillingTracker:
    """Resilience Cost Attribution Tracker delegating financial accounting to FinOpsManager."""

    def __init__(
        self,
        finops_manager: Optional[FinOpsManager] = None,
        tenant_guard: Optional[TenantAccessGuard] = None,
    ) -> None:
        self.finops_manager = finops_manager or FinOpsManager()
        self.tenant_guard = tenant_guard or TenantAccessGuard()

    def record_cost_event(
        self,
        tenant_id: str,
        resource_id: str,
        operation_type: str,
        cost_dollars: float,
    ) -> ResilienceCostEvent:
        event = ResilienceCostEvent(
            tenant_id=tenant_id,
            resource_id=resource_id,
            operation_type=operation_type,
            cost_dollars=cost_dollars,
        )

        try:
            self.finops_manager.record_cost(
                tenant_id=tenant_id,
                amount=cost_dollars,
                category="RESILIENCE_OPERATIONS",
                description=f"Resilience {operation_type} for {resource_id}",
            )
        except Exception:
            pass

        return event
