"""Schema evolution governance (Phase 5.43)."""

import uuid
from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from pydantic import BaseModel, Field

from app.data_intelligence.exceptions import (
    SchemaEvolutionException,
    HighRiskDataActionRequiresApprovalException,
    CrossTenantDataIntelligenceException,
)
from app.data_intelligence.schema import SchemaField, SchemaManager
from app.platform_contracts.delegation import DelegationRequest


class SchemaEvolutionRisk(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class SchemaEvolutionStatus(str, Enum):
    PROPOSED = "PROPOSED"
    REQUIRE_APPROVAL = "REQUIRE_APPROVAL"
    APPROVED = "APPROVED"
    DELEGATED = "DELEGATED"
    REJECTED = "REJECTED"


class SchemaEvolutionRequest(BaseModel):
    request_id: str
    dataset_id: str
    tenant_id: str
    target_fields: List[SchemaField]
    requested_by: str = "system"
    risk_level: SchemaEvolutionRisk = SchemaEvolutionRisk.LOW
    status: SchemaEvolutionStatus = SchemaEvolutionStatus.PROPOSED
    requires_approval: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class SchemaEvolutionPlan(BaseModel):
    plan_id: str
    request_id: str
    dataset_id: str
    tenant_id: str
    delegation_request: DelegationRequest
    status: SchemaEvolutionStatus
    summary: str


class SchemaEvolutionManager:
    """Manages schema evolution requests and delegates execution via DelegationRequest."""

    def __init__(self, schema_manager: Optional[SchemaManager] = None) -> None:
        self.schema_manager = schema_manager or SchemaManager()
        self._requests: Dict[str, SchemaEvolutionRequest] = {}
        self._plans: Dict[str, SchemaEvolutionPlan] = {}

    def propose_schema_evolution(
        self,
        dataset_id: str,
        tenant_id: str,
        target_fields: List[SchemaField],
        requested_by: str = "system",
        request_id: Optional[str] = None,
    ) -> SchemaEvolutionRequest:
        assessment = self.schema_manager.compare_schemas(dataset_id, tenant_id, target_fields)

        req_id = request_id or f"se-req-{uuid.uuid4().hex[:8]}"
        risk = SchemaEvolutionRisk.HIGH if assessment.is_breaking_change else SchemaEvolutionRisk.LOW
        requires_approval = (risk == SchemaEvolutionRisk.HIGH) or assessment.is_breaking_change

        status = SchemaEvolutionStatus.REQUIRE_APPROVAL if requires_approval else SchemaEvolutionStatus.PROPOSED

        req = SchemaEvolutionRequest(
            request_id=req_id,
            dataset_id=dataset_id,
            tenant_id=tenant_id,
            target_fields=target_fields,
            requested_by=requested_by,
            risk_level=risk,
            status=status,
            requires_approval=requires_approval,
        )
        self._requests[req_id] = req

        if requires_approval:
            raise HighRiskDataActionRequiresApprovalException(
                action_name="production_schema_migration",
                reason=f"Breaking schema change for dataset {dataset_id} requires approval.",
            )

        return req

    def execute_schema_evolution(
        self,
        request_id: str,
        tenant_id: str,
        approved: bool = False,
    ) -> SchemaEvolutionPlan:
        req = self._requests.get(request_id)
        if not req:
            raise SchemaEvolutionException(f"Schema evolution request '{request_id}' not found.")
        if req.tenant_id != tenant_id:
            raise CrossTenantDataIntelligenceException()

        if req.requires_approval and not approved:
            raise HighRiskDataActionRequiresApprovalException(
                action_name="production_schema_migration",
                reason="Schema evolution requires explicit approval.",
            )

        # Generate DelegationRequest instead of directly mutating schema
        del_req = DelegationRequest(
            delegation_id=f"del-se-{uuid.uuid4().hex[:8]}",
            tenant_id=tenant_id,
            target="ORCHESTRATION",
            action="apply_schema_migration",
            payload={
                "dataset_id": req.dataset_id,
                "target_fields": [f.model_dump() for f in req.target_fields],
            },
        )

        req.status = SchemaEvolutionStatus.DELEGATED
        plan_id = f"se-plan-{uuid.uuid4().hex[:8]}"

        plan = SchemaEvolutionPlan(
            plan_id=plan_id,
            request_id=request_id,
            dataset_id=req.dataset_id,
            tenant_id=tenant_id,
            delegation_request=del_req,
            status=SchemaEvolutionStatus.DELEGATED,
            summary=f"Delegated schema migration for dataset {req.dataset_id} via DelegationRequest {del_req.request_id}",
        )
        self._plans[plan_id] = plan
        return plan
