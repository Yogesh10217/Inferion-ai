"""AI Initiative Lifecycle Management Subsystem."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from app.portfolio_platform.exceptions import (
    CrossTenantPortfolioAccessException,
    InitiativeNotFoundException,
)


class InitiativeType(str, Enum):
    FOUNDATIONAL = "FOUNDATIONAL"
    APPLICATION = "APPLICATION"
    AUTOMATION = "AUTOMATION"
    GOVERNANCE = "GOVERNANCE"
    INFRASTRUCTURE = "INFRASTRUCTURE"


class InitiativeStatus(str, Enum):
    PROPOSED = "PROPOSED"
    QUALIFYING = "QUALIFYING"
    BUSINESS_CASE = "BUSINESS_CASE"
    PRIORITIZED = "PRIORITIZED"
    INVESTMENT_REVIEW = "INVESTMENT_REVIEW"
    APPROVAL_REQUIRED = "APPROVAL_REQUIRED"
    FUNDED = "FUNDED"
    DELEGATED = "DELEGATED"
    EXECUTING = "EXECUTING"
    MEASURING = "MEASURING"
    REALIZING_VALUE = "REALIZING_VALUE"
    COMPLETED = "COMPLETED"
    REJECTED = "REJECTED"
    ON_HOLD = "ON_HOLD"
    CANCELLED = "CANCELLED"


class InitiativePriority(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class InitiativeComplexity(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class InitiativeDependency(BaseModel):
    depends_on_initiative_id: str
    dependency_type: str = "BLOCKS"


class AIInitiative(BaseModel):
    initiative_id: str = Field(default_factory=lambda: f"init_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    opportunity_id: Optional[str] = None
    objective_id: Optional[str] = None
    title: str
    description: str
    initiative_type: InitiativeType = InitiativeType.APPLICATION
    status: InitiativeStatus = InitiativeStatus.PROPOSED
    priority: InitiativePriority = InitiativePriority.HIGH
    complexity: InitiativeComplexity = InitiativeComplexity.MEDIUM
    dependencies: List[InitiativeDependency] = Field(default_factory=list)
    owner_id: str = "program_manager"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class InitiativeManager:
    """Manages AI initiatives across their lifecycle."""

    def __init__(self) -> None:
        self._initiatives: Dict[str, AIInitiative] = {}

    def create_initiative(
        self,
        tenant_id: str,
        title: str,
        description: str,
        opportunity_id: Optional[str] = None,
        objective_id: Optional[str] = None,
        initiative_type: InitiativeType = InitiativeType.APPLICATION,
        priority: InitiativePriority = InitiativePriority.HIGH,
    ) -> AIInitiative:
        init = AIInitiative(
            tenant_id=tenant_id,
            title=title,
            description=description,
            opportunity_id=opportunity_id,
            objective_id=objective_id,
            initiative_type=initiative_type,
            priority=priority,
        )
        self._initiatives[init.initiative_id] = init
        return init

    def get_initiative(self, initiative_id: str, tenant_id: str) -> AIInitiative:
        init = self._initiatives.get(initiative_id)
        if not init:
            raise InitiativeNotFoundException(initiative_id=initiative_id, tenant_id=tenant_id)
        if init.tenant_id != tenant_id and tenant_id != "global":
            raise CrossTenantPortfolioAccessException(request_tenant=tenant_id, target_tenant=init.tenant_id, resource_id=initiative_id)
        return init

    def update_status(self, initiative_id: str, tenant_id: str, status: InitiativeStatus) -> AIInitiative:
        init = self.get_initiative(initiative_id, tenant_id)
        init.status = status
        init.updated_at = datetime.now(timezone.utc)
        return init

    def list_initiatives(self, tenant_id: str) -> List[AIInitiative]:
        return [i for i in self._initiatives.values() if i.tenant_id in (tenant_id, "global")]
