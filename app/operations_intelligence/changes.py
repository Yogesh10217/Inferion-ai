"""Change Intelligence & Operational Risk (Phase 5.41)."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict

from pydantic import BaseModel, Field

from app.operations_intelligence.exceptions import CrossTenantOperationsAccessException


class ChangeRisk(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ChangeImpact(str, Enum):
    MINOR = "MINOR"
    MAJOR = "MAJOR"
    SEVERE = "SEVERE"


class OperationalChange(BaseModel):
    change_id: str = Field(default_factory=lambda: f"chg_op_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    title: str
    target_service_id: str
    risk: ChangeRisk = ChangeRisk.MEDIUM
    impact: ChangeImpact = ChangeImpact.MINOR
    rollback_plan: str = ""
    is_evaluated: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ChangeIntelligenceManager:
    """Manages operational change references, impact, and rollback planning."""

    def __init__(self) -> None:
        self._changes: Dict[str, OperationalChange] = {}

    def register_change(
        self,
        tenant_id: str,
        title: str,
        target_service_id: str,
        rollback_plan: str = "",
        risk: ChangeRisk = ChangeRisk.MEDIUM,
        impact: ChangeImpact = ChangeImpact.MINOR,
    ) -> OperationalChange:
        chg = OperationalChange(
            tenant_id=tenant_id,
            title=title,
            target_service_id=target_service_id,
            rollback_plan=rollback_plan,
            risk=risk,
            impact=impact,
        )
        self._changes[chg.change_id] = chg
        return chg

    def get_change(self, tenant_id: str, change_id: str) -> OperationalChange:
        chg = self._changes.get(change_id)
        if not chg or chg.tenant_id != tenant_id:
            raise CrossTenantOperationsAccessException()
        return chg
