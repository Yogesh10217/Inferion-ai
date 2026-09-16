"""Budget & Funding Governance Subsystem."""

import hashlib
import json
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List

from pydantic import BaseModel, Field

from app.portfolio_platform.exceptions import (
    FundingDecisionException,
)


class FundingSource(str, Enum):
    STRATEGIC_AI_CAPEX = "STRATEGIC_AI_CAPEX"
    DEPARTMENT_OPEX = "DEPARTMENT_OPEX"
    INNOVATION_GRANT = "INNOVATION_GRANT"


class FundingStatus(str, Enum):
    REQUESTED = "REQUESTED"
    ALLOCATED = "ALLOCATED"
    REJECTED = "REJECTED"
    EXHAUSTED = "EXHAUSTED"


class BudgetEnvelope(BaseModel):
    envelope_id: str = Field(default_factory=lambda: f"env_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    total_budget_usd: float = 500000.0
    allocated_budget_usd: float = 0.0
    remaining_budget_usd: float = 500000.0


class FundingRequest(BaseModel):
    request_id: str = Field(default_factory=lambda: f"freq_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    initiative_id: str
    requested_amount_usd: float
    funding_source: FundingSource = FundingSource.STRATEGIC_AI_CAPEX
    status: FundingStatus = FundingStatus.REQUESTED
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class FundingAllocation(BaseModel):
    allocation_id: str = Field(default_factory=lambda: f"fund_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    initiative_id: str
    idempotency_key: str
    allocated_amount_usd: float
    funding_source: FundingSource = FundingSource.STRATEGIC_AI_CAPEX
    status: FundingStatus = FundingStatus.ALLOCATED
    allocation_fingerprint: str
    allocated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class FundingManager:
    """Manages budget envelopes, funding allocations, and enforces budget caps & idempotency."""

    def __init__(self) -> None:
        self._envelopes: Dict[str, BudgetEnvelope] = {}
        self._allocations: Dict[str, FundingAllocation] = {}
        self._idempotency_map: Dict[str, FundingAllocation] = {}

    def set_budget_envelope(self, tenant_id: str, total_budget_usd: float) -> BudgetEnvelope:
        env = self._envelopes.get(tenant_id)
        if not env:
            env = BudgetEnvelope(tenant_id=tenant_id, total_budget_usd=total_budget_usd, remaining_budget_usd=total_budget_usd)
            self._envelopes[tenant_id] = env
        else:
            env.total_budget_usd = total_budget_usd
            env.remaining_budget_usd = max(0.0, env.total_budget_usd - env.allocated_budget_usd)
        return env

    def get_budget_envelope(self, tenant_id: str) -> BudgetEnvelope:
        if tenant_id not in self._envelopes:
            return self.set_budget_envelope(tenant_id, 500000.0)
        return self._envelopes[tenant_id]

    def allocate_funding(
        self,
        tenant_id: str,
        initiative_id: str,
        idempotency_key: str,
        requested_amount_usd: float,
        funding_source: FundingSource = FundingSource.STRATEGIC_AI_CAPEX,
    ) -> FundingAllocation:
        # Idempotency check
        if idempotency_key in self._idempotency_map:
            return self._idempotency_map[idempotency_key]

        env = self.get_budget_envelope(tenant_id)
        if requested_amount_usd > env.remaining_budget_usd:
            raise FundingDecisionException(
                f"Funding Request Denied: Requested ${requested_amount_usd:,.2f} exceeds remaining budget of ${env.remaining_budget_usd:,.2f} for tenant '{tenant_id}'."
            )

        canonical_str = json.dumps(
            {"tenant": tenant_id, "initiative": initiative_id, "amount": requested_amount_usd, "idemp": idempotency_key},
            sort_keys=True,
        )
        fingerprint = hashlib.sha256(canonical_str.encode("utf-8")).hexdigest()

        alloc = FundingAllocation(
            tenant_id=tenant_id,
            initiative_id=initiative_id,
            idempotency_key=idempotency_key,
            allocated_amount_usd=requested_amount_usd,
            funding_source=funding_source,
            status=FundingStatus.ALLOCATED,
            allocation_fingerprint=fingerprint,
        )

        env.allocated_budget_usd += requested_amount_usd
        env.remaining_budget_usd -= requested_amount_usd

        self._allocations[alloc.allocation_id] = alloc
        self._idempotency_map[idempotency_key] = alloc
        return alloc

    def list_allocations(self, tenant_id: str) -> List[FundingAllocation]:
        return [a for a in self._allocations.values() if a.tenant_id == tenant_id]
