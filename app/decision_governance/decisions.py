"""Enterprise decision lifecycle and core decision entities."""

import hashlib
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.decision_governance.exceptions import (
    CrossTenantDecisionGovernanceException,
    DecisionNotFoundException,
    ImmutableDecisionRecordException,
)


class DecisionType(str, Enum):
    INFRASTRUCTURE = "INFRASTRUCTURE"
    ACCESS = "ACCESS"
    COST = "COST"
    MODEL = "MODEL"
    DATA = "DATA"
    WORKFLOW = "WORKFLOW"
    COMPLIANCE = "COMPLIANCE"
    SECURITY = "SECURITY"
    OPERATIONAL = "OPERATIONAL"
    STRATEGIC = "STRATEGIC"


class DecisionStatus(str, Enum):
    DRAFT = "DRAFT"
    ANALYZING = "ANALYZING"
    RECOMMENDED = "RECOMMENDED"
    REQUIRES_APPROVAL = "REQUIRES_APPROVAL"
    APPROVED = "APPROVED"
    DELEGATED = "DELEGATED"
    VERIFIED = "VERIFIED"
    FINALIZED = "FINALIZED"


class DecisionPriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"
    URGENT = "URGENT"


class DecisionOutcome(str, Enum):
    ALLOW = "ALLOW"
    DENY = "DENY"
    REQUIRE_APPROVAL = "REQUIRE_APPROVAL"
    RESTRICT = "RESTRICT"
    BLOCK = "BLOCK"


class DecisionFactor(BaseModel):
    name: str
    weight: float = 1.0
    impact_score: float = 0.0
    description: str = ""
    domain: str = "general"
    metadata: Dict[str, Any] = Field(default_factory=dict)


class DecisionContext(BaseModel):
    tenant_id: str
    domain: str = "operations"
    initiator_id: str = "system"
    target_resource_id: Optional[str] = None
    target_resource_type: Optional[str] = None
    environment: str = "production"
    signals: List[Dict[str, Any]] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class Decision(BaseModel):
    decision_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    title: str
    description: str = ""
    decision_type: DecisionType = DecisionType.OPERATIONAL
    status: DecisionStatus = DecisionStatus.DRAFT
    priority: DecisionPriority = DecisionPriority.MEDIUM
    outcome: Optional[DecisionOutcome] = None
    context: DecisionContext
    factors: List[DecisionFactor] = Field(default_factory=list)
    confidence: float = 0.0
    risk_score: float = 0.0
    fingerprint: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    finalized_at: Optional[datetime] = None
    is_immutable: bool = False
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def calculate_fingerprint(self) -> str:
        data = f"{self.decision_id}:{self.tenant_id}:{self.status.value}:{self.outcome.value if self.outcome else ''}:{self.created_at.isoformat()}"
        return hashlib.sha256(data.encode("utf-8")).hexdigest()


class DecisionManager:
    """Manages the creation, status transitions, and immutability of decisions."""

    def __init__(self, repository: Optional[Any] = None) -> None:
        self._decisions: Dict[str, Decision] = {}
        self.repository = repository

    def create_decision(
        self,
        tenant_id: str,
        title: str,
        decision_type: DecisionType,
        context: DecisionContext,
        description: str = "",
        priority: DecisionPriority = DecisionPriority.MEDIUM,
        factors: Optional[List[DecisionFactor]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Decision:
        decision = Decision(
            tenant_id=tenant_id,
            title=title,
            description=description,
            decision_type=decision_type,
            status=DecisionStatus.DRAFT,
            priority=priority,
            context=context,
            factors=factors or [],
            metadata=metadata or {},
        )
        decision.fingerprint = decision.calculate_fingerprint()
        self._decisions[decision.decision_id] = decision
        return decision

    def get_decision(self, decision_id: str, tenant_id: str) -> Decision:
        decision = self._decisions.get(decision_id)
        if not decision:
            raise DecisionNotFoundException(f"Decision '{decision_id}' not found")
        if decision.tenant_id != tenant_id:
            raise CrossTenantDecisionGovernanceException()
        return decision

    def update_status(
        self, decision_id: str, tenant_id: str, new_status: DecisionStatus, outcome: Optional[DecisionOutcome] = None
    ) -> Decision:
        decision = self.get_decision(decision_id, tenant_id)
        if decision.is_immutable:
            raise ImmutableDecisionRecordException(f"Decision '{decision_id}' is finalized and immutable")
        decision.status = new_status
        if outcome:
            decision.outcome = outcome
        decision.updated_at = datetime.now(timezone.utc)
        decision.fingerprint = decision.calculate_fingerprint()

        if new_status == DecisionStatus.FINALIZED:
            decision.is_immutable = True
            decision.finalized_at = decision.updated_at

        return decision

    def list_decisions(self, tenant_id: str) -> List[Decision]:
        return [d for d in self._decisions.values() if d.tenant_id == tenant_id]
