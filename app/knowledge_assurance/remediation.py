"""Knowledge Assurance Remediation Module.

Provides remediation plan generation and execution via delegation requests.
Strictly prohibits direct external state mutations.
"""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from app.knowledge_assurance.exceptions import (
    CrossTenantKnowledgeAssuranceException,
    HighRiskKnowledgeActionRequiresApprovalException,
    KnowledgeReferenceNotFoundException,
)
from app.platform_contracts.delegation import DelegationRequest, DelegationTarget
from app.approvals.approval_engine import ApprovalEngine
from app.governance_platform.risk import RiskManager


class KnowledgeRemediationPriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class KnowledgeRemediationStatus(str, Enum):
    DRAFT = "DRAFT"
    PROPOSED = "PROPOSED"
    APPROVED = "APPROVED"
    DELEGATED = "DELEGATED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class KnowledgeRemediationAction(BaseModel):
    action_id: str = Field(default_factory=lambda: f"act-{uuid.uuid4().hex[:8]}")
    action_type: str  # REFRESH_SOURCE, RESOLVE_CONFLICT, FILL_GAP, DEDUPLICATE, ARCHIVE_STALE
    target_resource_id: str
    description: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    requires_approval: bool = False
    delegation_request_id: Optional[str] = None


class KnowledgeRemediationPlan(BaseModel):
    plan_id: str = Field(default_factory=lambda: f"rem-{uuid.uuid4().hex[:8]}")
    tenant_id: str
    target_resource_id: str
    priority: KnowledgeRemediationPriority = KnowledgeRemediationPriority.MEDIUM
    status: KnowledgeRemediationStatus = KnowledgeRemediationStatus.DRAFT
    actions: List[KnowledgeRemediationAction] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class KnowledgeRemediationManager:
    """Manages remediation planning and delegation."""

    def __init__(
        self,
        risk_manager: Optional[RiskManager] = None,
        approval_engine: Optional[ApprovalEngine] = None,
    ) -> None:
        self.risk_manager = risk_manager or RiskManager()
        self.approval_engine = approval_engine or ApprovalEngine()
        self._plans: Dict[str, KnowledgeRemediationPlan] = {}
        self._delegation_requests: Dict[str, DelegationRequest] = {}

    def create_remediation_plan(
        self,
        tenant_id: str,
        target_resource_id: str,
        priority: KnowledgeRemediationPriority = KnowledgeRemediationPriority.MEDIUM,
        actions: Optional[List[Dict[str, Any]]] = None,
    ) -> KnowledgeRemediationPlan:
        action_objects: List[KnowledgeRemediationAction] = []
        if actions:
            for act in actions:
                req_app = act.get("requires_approval", False)
                if priority in [KnowledgeRemediationPriority.HIGH, KnowledgeRemediationPriority.CRITICAL]:
                    req_app = True
                action_objects.append(
                    KnowledgeRemediationAction(
                        action_type=act.get("action_type", "GENERIC_REMEDIATION"),
                        target_resource_id=act.get("target_resource_id", target_resource_id),
                        description=act.get("description", "Remediation action"),
                        parameters=act.get("parameters", {}),
                        requires_approval=req_app,
                    )
                )

        plan = KnowledgeRemediationPlan(
            tenant_id=tenant_id,
            target_resource_id=target_resource_id,
            priority=priority,
            actions=action_objects,
        )
        self._plans[plan.plan_id] = plan
        return plan

    def execute_plan_via_delegation(
        self, tenant_id: str, plan_id: str
    ) -> Dict[str, Any]:
        plan = self.get_plan(tenant_id, plan_id)

        if plan.priority == KnowledgeRemediationPriority.CRITICAL:
            raise HighRiskKnowledgeActionRequiresApprovalException(
                "Critical remediation plans require explicit governance approval."
            )

        delegation_requests: List[DelegationRequest] = []
        for action in plan.actions:
            del_req = DelegationRequest(
                tenant_id=tenant_id,
                target=DelegationTarget.ORCHESTRATION,
                action=action.action_type,
                payload={
                    "plan_id": plan.plan_id,
                    "action_id": action.action_id,
                    "target_resource_id": action.target_resource_id,
                    "params": action.parameters,
                },
            )
            action.delegation_request_id = del_req.request_id
            self._delegation_requests[del_req.request_id] = del_req
            delegation_requests.append(del_req)

        plan.status = KnowledgeRemediationStatus.DELEGATED
        plan.updated_at = datetime.now(timezone.utc)

        return {
            "plan_id": plan.plan_id,
            "status": plan.status.value,
            "delegated_actions_count": len(delegation_requests),
            "delegation_requests": [req.request_id for req in delegation_requests],
        }

    def get_plan(self, tenant_id: str, plan_id: str) -> KnowledgeRemediationPlan:
        if plan_id not in self._plans:
            raise KnowledgeReferenceNotFoundException(f"Remediation plan {plan_id} not found.")
        plan = self._plans[plan_id]
        if plan.tenant_id != tenant_id:
            raise CrossTenantKnowledgeAssuranceException()
        return plan

    def list_plans(self, tenant_id: str) -> List[KnowledgeRemediationPlan]:
        return [plan for plan in self._plans.values() if plan.tenant_id == tenant_id]
