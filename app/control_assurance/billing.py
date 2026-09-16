"""Control Assurance Cost Attribution Subsystem (Phase 5.38)."""

import uuid
from datetime import datetime, timezone
from typing import Dict, Optional

from pydantic import BaseModel, Field

from app.finops.manager import FinOpsManager
from app.platform_contracts.tenant import TenantAccessGuard


class ControlAssuranceCostEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: f"cbill_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    control_id: str
    operation: str
    cost_usd: float = 0.01
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ControlAssuranceBillingTracker:
    """Tracks and attributes control assurance operations costs via FinOps."""

    def __init__(self, tenant_guard: Optional[TenantAccessGuard] = None) -> None:
        self.tenant_guard = tenant_guard or TenantAccessGuard()
        self.finops_manager = FinOpsManager()
        self._events: Dict[str, ControlAssuranceCostEvent] = {}

    def record_cost_event(
        self,
        tenant_id: str,
        control_id: str,
        operation: str,
        cost_usd: float = 0.01,
    ) -> ControlAssuranceCostEvent:
        ev = ControlAssuranceCostEvent(
            tenant_id=tenant_id,
            control_id=control_id,
            operation=operation,
            cost_usd=cost_usd,
        )
        self._events[ev.event_id] = ev
        return ev
