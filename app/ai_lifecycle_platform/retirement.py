"""AI Asset Retirement Subsystem (Phase 5.33)."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

from app.ai_lifecycle_platform.exceptions import CrossTenantLifecycleAccessException, ImmutableLifecycleRecordException
from app.platform_contracts.delegation import DelegationRequest, DelegationTarget
from app.platform_contracts.fingerprinting import FingerprintGenerator
from app.platform_contracts.immutability import ImmutableResource, ImmutableResourceState, ImmutableResourceValidator


class RetirementStatus(str, Enum):
    REQUESTED = "REQUESTED"
    IMPACT_ANALYSIS = "IMPACT_ANALYSIS"
    DEPENDENCY_ANALYSIS = "DEPENDENCY_ANALYSIS"
    APPROVAL = "APPROVAL"
    DELEGATED_EXECUTION = "DELEGATED_EXECUTION"
    VERIFICATION = "VERIFICATION"
    RETIRED = "RETIRED"
    IMMUTABLE_SNAPSHOT = "IMMUTABLE_SNAPSHOT"


class RetirementReason(str, Enum):
    DEPRECATED = "DEPRECATED"
    SECURITY_VULNERABILITY = "SECURITY_VULNERABILITY"
    REPLACED = "REPLACED"
    COST_OPTIMIZATION = "COST_OPTIMIZATION"


class RetirementPlan(BaseModel):
    plan_id: str = Field(default_factory=lambda: f"retplan_{uuid.uuid4().hex[:12]}")
    asset_id: str
    impact_score: float = 15.0
    active_dependencies_count: int = 0
    delegation_request: DelegationRequest


class RetirementRequest(BaseModel):
    retirement_id: str = Field(default_factory=lambda: f"ret_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    asset_id: str
    reason: RetirementReason = RetirementReason.DEPRECATED
    status: RetirementStatus = RetirementStatus.REQUESTED
    plan: Optional[RetirementPlan] = None
    immutable_record: ImmutableResource = Field(default_factory=lambda: ImmutableResource(resource_id="", tenant_id=""))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def model_post_init(self, __context: Any) -> None:
        if not self.immutable_record.resource_id:
            self.immutable_record = ImmutableResource(resource_id=self.retirement_id, tenant_id=self.tenant_id)


class RetirementManager:
    """Manages AI asset retirement workflow and generates immutable final snapshots."""

    def __init__(self) -> None:
        self._retirements: Dict[str, RetirementRequest] = {}

    def request_retirement(
        self,
        tenant_id: str,
        asset_id: str,
        reason: RetirementReason = RetirementReason.DEPRECATED,
    ) -> RetirementRequest:
        delegation = DelegationRequest(
            tenant_id=tenant_id,
            target=DelegationTarget.PLATFORM_OPERATIONS,
            action="RETIRE_AI_ASSET",
            payload={"asset_id": asset_id, "reason": reason.value},
        )
        plan = RetirementPlan(asset_id=asset_id, delegation_request=delegation)

        req = RetirementRequest(
            tenant_id=tenant_id,
            asset_id=asset_id,
            reason=reason,
            status=RetirementStatus.REQUESTED,
            plan=plan,
        )
        self._retirements[req.retirement_id] = req
        return req

    def finalize_retirement(self, retirement_id: str, tenant_id: str) -> RetirementRequest:
        req = self._retirements.get(retirement_id)
        if not req:
            raise KeyError(f"Retirement '{retirement_id}' not found.")
        if tenant_id != "global" and req.tenant_id != "global" and tenant_id != req.tenant_id:
            raise CrossTenantLifecycleAccessException(tenant_id, req.tenant_id)

        if req.immutable_record.state == ImmutableResourceState.FINALIZED:
            raise ImmutableLifecycleRecordException(retirement_id)

        req.status = RetirementStatus.RETIRED
        fp = FingerprintGenerator.generate(req.model_dump(exclude={"immutable_record"}))
        ImmutableResourceValidator.finalize(req.immutable_record, fingerprint=fp)
        return req

    def get_retirement(self, retirement_id: str, tenant_id: str) -> RetirementRequest:
        req = self._retirements.get(retirement_id)
        if not req:
            raise KeyError(f"Retirement '{retirement_id}' not found.")
        if tenant_id != "global" and req.tenant_id != "global" and tenant_id != req.tenant_id:
            raise CrossTenantLifecycleAccessException(tenant_id, req.tenant_id)
        return req
