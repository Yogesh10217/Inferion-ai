"""Delegation-Only Decision Execution Subsystem."""

from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.decision_intelligence.exceptions import DecisionIntelligenceException, CrossTenantDecisionAccessException


class DelegationTarget(str, Enum):
    PLATFORM_OPERATIONS = "PLATFORM_OPERATIONS"
    APPLICATION_PLATFORM = "APPLICATION_PLATFORM"
    DEVELOPER_PLATFORM = "DEVELOPER_PLATFORM"
    ORCHESTRATION = "ORCHESTRATION"
    PORTFOLIO_PLATFORM = "PORTFOLIO_PLATFORM"
    ARCHITECTURE_PLATFORM = "ARCHITECTURE_PLATFORM"
    DATA_GOVERNANCE = "DATA_GOVERNANCE"
    COMPLIANCE_PLATFORM = "COMPLIANCE_PLATFORM"


class DelegationStatus(str, Enum):
    PLANNED = "PLANNED"
    DELEGATED = "DELEGATED"
    EXECUTING = "EXECUTING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class DecisionDelegationPlan(BaseModel):
    delegation_id: str = Field(default_factory=lambda: f"del_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    decision_id: str
    target: DelegationTarget = DelegationTarget.PORTFOLIO_PLATFORM
    status: DelegationStatus = DelegationStatus.PLANNED
    delegated_reference_id: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DecisionDelegationManager:
    """Delegates approved decision execution plans to existing platform managers."""

    def __init__(self) -> None:
        self._plans: Dict[str, DecisionDelegationPlan] = {}

    def create_delegation_plan(
        self,
        tenant_id: str,
        decision_id: str,
        target: DelegationTarget = DelegationTarget.PORTFOLIO_PLATFORM,
    ) -> DecisionDelegationPlan:
        plan = DecisionDelegationPlan(
            tenant_id=tenant_id,
            decision_id=decision_id,
            target=target,
        )
        self._plans[plan.delegation_id] = plan
        return plan

    def delegate_execution(
        self,
        delegation_id: str,
        tenant_id: str,
        target_manager_name: str = "PortfolioPlatformManager",
    ) -> DecisionDelegationPlan:
        plan = self._plans.get(delegation_id)
        if not plan or (plan.tenant_id != tenant_id and tenant_id != "global"):
            raise CrossTenantDecisionAccessException(tenant_id, plan.tenant_id if plan else "unknown")

        plan.status = DelegationStatus.DELEGATED
        plan.delegated_reference_id = f"delref_{target_manager_name}_{uuid.uuid4().hex[:8]}"
        plan.status = DelegationStatus.COMPLETED
        return plan
