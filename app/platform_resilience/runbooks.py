"""Operational Runbook Intelligence Subsystem (Phase 5.37)."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.platform_contracts.tenant import TenantAccessGuard
from app.platform_resilience.exceptions import (
    CrossTenantResilienceAccessException,
    ImmutableResilienceRecordException,
    ResilienceResourceNotFoundException,
)


class RunbookStatus(str, Enum):
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    FINALIZED = "FINALIZED"
    DEPRECATED = "DEPRECATED"


class RunbookTrigger(str, Enum):
    MANUAL = "MANUAL"
    SLO_BREACH = "SLO_BREACH"
    CAPACITY_SATURATION = "CAPACITY_SATURATION"
    INCIDENT_DETECTED = "INCIDENT_DETECTED"
    REGION_FAILURE = "REGION_FAILURE"


class RunbookStep(BaseModel):
    step_number: int
    name: str
    target_system: str = "PLATFORM_OPERATIONS"
    action_payload: Dict[str, Any] = Field(default_factory=dict)


class RunbookExecutionPlan(BaseModel):
    execution_plan_id: str = Field(default_factory=lambda: f"rbexec_{uuid.uuid4().hex[:12]}")
    runbook_id: str
    tenant_id: str
    steps: List[RunbookStep] = Field(default_factory=list)
    status: str = "PLANNED"


class OperationalRunbook(BaseModel):
    runbook_id: str = Field(default_factory=lambda: f"runbook_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    title: str
    trigger: RunbookTrigger = RunbookTrigger.INCIDENT_DETECTED
    steps: List[RunbookStep] = Field(default_factory=list)
    is_immutable: bool = False
    status: RunbookStatus = RunbookStatus.DRAFT
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class RunbookManager:
    """Operational Runbook Intelligence Manager maintaining immutable finalized runbooks."""

    def __init__(self, tenant_guard: Optional[TenantAccessGuard] = None) -> None:
        self.tenant_guard = tenant_guard or TenantAccessGuard()
        self._runbooks: Dict[str, OperationalRunbook] = {}

    def create_runbook(
        self,
        tenant_id: str,
        title: str,
        trigger: RunbookTrigger = RunbookTrigger.INCIDENT_DETECTED,
        steps: Optional[List[RunbookStep]] = None,
    ) -> OperationalRunbook:
        rb = OperationalRunbook(
            tenant_id=tenant_id,
            title=title,
            trigger=trigger,
            steps=steps
            or [
                RunbookStep(step_number=1, name="Check service health metrics"),
                RunbookStep(step_number=2, name="Isolate degraded worker nodes"),
                RunbookStep(step_number=3, name="Scale out replica pool"),
            ],
        )
        self._runbooks[rb.runbook_id] = rb
        return rb

    def finalize_runbook(self, runbook_id: str, tenant_id: str) -> OperationalRunbook:
        rb = self.get_runbook(runbook_id, tenant_id)
        rb.status = RunbookStatus.FINALIZED
        rb.is_immutable = True
        rb.updated_at = datetime.now(timezone.utc)
        return rb

    def add_step_to_runbook(self, runbook_id: str, tenant_id: str, step: RunbookStep) -> OperationalRunbook:
        rb = self.get_runbook(runbook_id, tenant_id)
        if rb.is_immutable or rb.status == RunbookStatus.FINALIZED:
            raise ImmutableResilienceRecordException(
                f"Runbook '{runbook_id}' is finalized and immutable. Cannot modify steps."
            )

        rb.steps.append(step)
        rb.updated_at = datetime.now(timezone.utc)
        return rb

    def get_runbook(self, runbook_id: str, tenant_id: str) -> OperationalRunbook:
        rb = self._runbooks.get(runbook_id)
        if not rb:
            raise ResilienceResourceNotFoundException(runbook_id)

        try:
            self.tenant_guard.enforce_isolation(tenant_id, rb.tenant_id)
        except Exception:
            raise CrossTenantResilienceAccessException(tenant_id, rb.tenant_id)

        return rb
