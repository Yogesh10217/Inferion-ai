"""Data remediation intelligence (Phase 5.43)."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.data_intelligence.exceptions import (
    CrossTenantDataIntelligenceException,
    HighRiskDataActionRequiresApprovalException,
)
from app.platform_contracts.delegation import DelegationRequest, DelegationTarget


class DataRemediationPriority(str, Enum):
    P4_LOW = "P4_LOW"
    P3_MEDIUM = "P3_MEDIUM"
    P2_HIGH = "P2_HIGH"
    P1_CRITICAL = "P1_CRITICAL"


class DataRemediationStatus(str, Enum):
    PROPOSED = "PROPOSED"
    REQUIRE_APPROVAL = "REQUIRE_APPROVAL"
    APPROVED = "APPROVED"
    DELEGATED = "DELEGATED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    REJECTED = "REJECTED"


class DataRemediationAction(BaseModel):
    action_id: str
    action_type: str  # PIPELINE_RESTART, DATA_REPAIR, DATASET_ROLLBACK, SCHEMA_MIGRATION, REPROCESSING
    target_subsystem: str  # data_fabric, mlops, orchestration
    params: Dict[str, Any] = Field(default_factory=dict)
    is_high_risk: bool = False


class DataRemediationPlan(BaseModel):
    plan_id: str
    incident_id: str
    dataset_id: str
    tenant_id: str
    priority: DataRemediationPriority
    actions: List[DataRemediationAction] = Field(default_factory=list)
    status: DataRemediationStatus = DataRemediationStatus.PROPOSED
    delegation_requests: List[DelegationRequest] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DataRemediationManager:
    """Manages data remediation plans by recommending and delegating actions via DelegationRequest."""

    def __init__(self) -> None:
        self._plans: Dict[str, DataRemediationPlan] = {}

    def create_remediation_plan(
        self,
        incident_id: str,
        dataset_id: str,
        tenant_id: str,
        priority: DataRemediationPriority,
        actions: List[DataRemediationAction],
        plan_id: Optional[str] = None,
    ) -> DataRemediationPlan:
        pid = plan_id or f"rem-plan-{uuid.uuid4().hex[:8]}"

        has_high_risk = any(
            a.is_high_risk or a.action_type in ("DATASET_ROLLBACK", "DATA_REPAIR", "DATA_DELETION") for a in actions
        )
        status = DataRemediationStatus.REQUIRE_APPROVAL if has_high_risk else DataRemediationStatus.PROPOSED

        plan = DataRemediationPlan(
            plan_id=pid,
            incident_id=incident_id,
            dataset_id=dataset_id,
            tenant_id=tenant_id,
            priority=priority,
            actions=actions,
            status=status,
        )
        self._plans[pid] = plan

        if has_high_risk:
            raise HighRiskDataActionRequiresApprovalException(
                action_name=actions[0].action_type if actions else "remediation",
                reason=f"High-risk remediation action for incident {incident_id} requires human approval.",
            )

        return plan

    def execute_remediation(
        self,
        plan_id: str,
        tenant_id: str,
        approved: bool = False,
    ) -> DataRemediationPlan:
        plan = self.get_plan(plan_id, tenant_id)

        has_high_risk = any(
            a.is_high_risk or a.action_type in ("DATASET_ROLLBACK", "DATA_REPAIR", "DATA_DELETION")
            for a in plan.actions
        )

        if has_high_risk and not approved:
            raise HighRiskDataActionRequiresApprovalException(
                action_name=plan.actions[0].action_type if plan.actions else "remediation",
                reason="High-risk remediation action requires explicit human approval.",
            )

        del_requests = []
        for action in plan.actions:
            target_name = action.target_subsystem.upper()
            if target_name not in (
                "PLATFORM_OPERATIONS",
                "APPLICATION_PLATFORM",
                "DEVELOPER_PLATFORM",
                "ORCHESTRATION",
                "INTEGRATION",
                "ARCHITECTURE_PLATFORM",
                "PORTFOLIO_PLATFORM",
            ):
                target_name = "ORCHESTRATION"
            del_req = DelegationRequest(
                delegation_id=f"del-rem-{uuid.uuid4().hex[:8]}",
                tenant_id=tenant_id,
                target=DelegationTarget(target_name),
                action=action.action_type.lower(),
                payload={
                    "dataset_id": plan.dataset_id,
                    "incident_id": plan.incident_id,
                    "params": action.params,
                },
            )
            del_requests.append(del_req)

        plan.delegation_requests = del_requests
        plan.status = DataRemediationStatus.DELEGATED
        return plan

    def get_plan(self, plan_id: str, tenant_id: str) -> DataRemediationPlan:
        plan = self._plans.get(plan_id)
        if not plan:
            raise Exception(f"Remediation plan '{plan_id}' not found.")
        if plan.tenant_id != tenant_id:
            raise CrossTenantDataIntelligenceException()
        return plan
