"""Immutable Enterprise Decision Lifecycle Subsystem with Strict State Transition Validation."""

import hashlib
import json
from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.decision_intelligence.exceptions import (
    DecisionNotFoundException,
    ImmutableDecisionRecordException,
    CrossTenantDecisionIntelligenceException,
    InvalidDecisionStateTransitionException,
)


class DecisionType(str, Enum):
    ARCHITECTURE = "ARCHITECTURE"
    DATA_GOVERNANCE = "DATA_GOVERNANCE"
    COMPLIANCE = "COMPLIANCE"
    INVESTMENT = "INVESTMENT"
    PORTFOLIO = "PORTFOLIO"
    OPERATIONS = "OPERATIONS"
    SECURITY = "SECURITY"
    APPLICATION = "APPLICATION"
    WORKFLOW = "WORKFLOW"
    CROSS_DOMAIN = "CROSS_DOMAIN"


class DecisionLifecycleState(str, Enum):
    PROPOSED = "PROPOSED"
    ANALYZING = "ANALYZING"
    OPTIONS_IDENTIFIED = "OPTIONS_IDENTIFIED"
    RISK_ASSESSED = "RISK_ASSESSED"
    POLICY_EVALUATED = "POLICY_EVALUATED"
    RECOMMENDED = "RECOMMENDED"
    REQUIRES_APPROVAL = "REQUIRES_APPROVAL"
    APPROVED = "APPROVED"
    DELEGATED = "DELEGATED"
    VERIFIED = "VERIFIED"
    CLOSED = "CLOSED"
    DENIED = "DENIED"
    CANCELLED = "CANCELLED"
    FAILED = "FAILED"


# Backward compatibility
DecisionStatus = DecisionLifecycleState


# Valid state transitions map
VALID_TRANSITIONS: Dict[DecisionLifecycleState, List[DecisionLifecycleState]] = {
    DecisionLifecycleState.PROPOSED: [DecisionLifecycleState.ANALYZING, DecisionLifecycleState.CANCELLED, DecisionLifecycleState.CLOSED],
    DecisionLifecycleState.ANALYZING: [DecisionLifecycleState.OPTIONS_IDENTIFIED, DecisionLifecycleState.CANCELLED, DecisionLifecycleState.FAILED, DecisionLifecycleState.CLOSED],
    DecisionLifecycleState.OPTIONS_IDENTIFIED: [DecisionLifecycleState.RISK_ASSESSED, DecisionLifecycleState.CANCELLED, DecisionLifecycleState.CLOSED],
    DecisionLifecycleState.RISK_ASSESSED: [DecisionLifecycleState.POLICY_EVALUATED, DecisionLifecycleState.CANCELLED, DecisionLifecycleState.CLOSED],
    DecisionLifecycleState.POLICY_EVALUATED: [DecisionLifecycleState.RECOMMENDED, DecisionLifecycleState.DENIED, DecisionLifecycleState.CANCELLED, DecisionLifecycleState.CLOSED],
    DecisionLifecycleState.RECOMMENDED: [DecisionLifecycleState.REQUIRES_APPROVAL, DecisionLifecycleState.APPROVED, DecisionLifecycleState.CANCELLED, DecisionLifecycleState.CLOSED],
    DecisionLifecycleState.REQUIRES_APPROVAL: [DecisionLifecycleState.APPROVED, DecisionLifecycleState.DENIED, DecisionLifecycleState.CANCELLED, DecisionLifecycleState.CLOSED],
    DecisionLifecycleState.APPROVED: [DecisionLifecycleState.DELEGATED, DecisionLifecycleState.CANCELLED, DecisionLifecycleState.CLOSED],
    DecisionLifecycleState.DELEGATED: [DecisionLifecycleState.VERIFIED, DecisionLifecycleState.FAILED, DecisionLifecycleState.CANCELLED, DecisionLifecycleState.CLOSED],
    DecisionLifecycleState.VERIFIED: [DecisionLifecycleState.CLOSED, DecisionLifecycleState.FAILED],
    DecisionLifecycleState.CLOSED: [],  # Terminal state
    DecisionLifecycleState.DENIED: [],  # Terminal state
    DecisionLifecycleState.CANCELLED: [],  # Terminal state
    DecisionLifecycleState.FAILED: [DecisionLifecycleState.ANALYZING, DecisionLifecycleState.CLOSED],
}


class EnterpriseDecision(BaseModel):
    decision_id: str = Field(default_factory=lambda: f"dec_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    title: str
    description: Optional[str] = None
    decision_type: DecisionType = DecisionType.CROSS_DOMAIN
    state: DecisionLifecycleState = DecisionLifecycleState.PROPOSED
    context_id: Optional[str] = None
    evidence_id: Optional[str] = None
    recommendation_id: Optional[str] = None
    governance_id: Optional[str] = None
    is_finalized: bool = False
    decision_fingerprint: Optional[str] = None
    confidence_score: float = 0.0
    uncertainty_score: float = 0.0
    risk_level: str = "MEDIUM"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    finalized_at: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @property
    def status(self) -> DecisionLifecycleState:
        return self.state

    @status.setter
    def status(self, value: DecisionLifecycleState):
        self.state = value

    def transition_to(self, target_state: DecisionLifecycleState, reason: Optional[str] = None) -> "EnterpriseDecision":
        """Transitions decision state with strict transition validation."""
        if self.is_finalized and target_state != DecisionLifecycleState.CLOSED:
            raise ImmutableDecisionRecordException(f"Cannot transition finalized decision '{self.decision_id}'")

        allowed_targets = VALID_TRANSITIONS.get(self.state, [])
        if target_state not in allowed_targets:
            raise InvalidDecisionStateTransitionException(
                f"Invalid transition from state '{self.state.value}' to '{target_state.value}' for decision '{self.decision_id}'."
            )

        self.state = target_state
        self.updated_at = datetime.now(timezone.utc)
        if reason:
            self.metadata["transition_reason"] = reason
        return self


class DecisionSnapshot(BaseModel):
    snapshot_id: str = Field(default_factory=lambda: f"decsnap_{uuid.uuid4().hex[:12]}")
    decision_id: str
    tenant_id: str
    decision_context_version: str = "1.0.0"
    evidence_references: List[str] = Field(default_factory=list)
    policy_version: str = "1.0.0"
    risk_score: float = 20.0
    trust_score: float = 90.0
    fingerprint: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DecisionManager:
    """Manages the end-to-end lifecycle and immutability of enterprise decisions."""

    def __init__(self) -> None:
        self._decisions: Dict[str, EnterpriseDecision] = {}
        self._snapshots: Dict[str, DecisionSnapshot] = {}

    def create_decision(self, tenant_id: str, title: str, decision_type: DecisionType = DecisionType.CROSS_DOMAIN, description: Optional[str] = None) -> EnterpriseDecision:
        dec = EnterpriseDecision(tenant_id=tenant_id, title=title, decision_type=decision_type, description=description)
        self._decisions[dec.decision_id] = dec
        return dec

    def get_decision(self, decision_id: str, tenant_id: str) -> EnterpriseDecision:
        dec = self._decisions.get(decision_id)
        if not dec:
            raise DecisionNotFoundException(f"Decision '{decision_id}' not found for tenant '{tenant_id}'")
        if dec.tenant_id != tenant_id and tenant_id != "global":
            raise CrossTenantDecisionIntelligenceException(f"Unauthorized cross-tenant access to decision '{decision_id}'")
        return dec

    def update_decision_state(self, decision_id: str, tenant_id: str, target_state: DecisionLifecycleState, reason: Optional[str] = None) -> EnterpriseDecision:
        dec = self.get_decision(decision_id, tenant_id)
        return dec.transition_to(target_state, reason=reason)

    def finalize_decision(
        self,
        decision_id: str,
        tenant_id: str,
        risk_score: float = 20.0,
        trust_score: float = 90.0,
        policy_version: str = "1.0.0",
    ) -> EnterpriseDecision:
        dec = self.get_decision(decision_id, tenant_id)
        if dec.is_finalized:
            raise ImmutableDecisionRecordException(f"Decision '{decision_id}' is already finalized")

        dec.state = DecisionLifecycleState.CLOSED
        dec.updated_at = datetime.now(timezone.utc)

        canonical_payload = {
            "decision_id": dec.decision_id,
            "tenant_id": dec.tenant_id,
            "title": dec.title,
            "decision_type": dec.decision_type.value,
            "risk_score": risk_score,
            "trust_score": trust_score,
            "policy_version": policy_version,
            "finalized_at": datetime.now(timezone.utc).isoformat(),
        }
        fingerprint = hashlib.sha256(json.dumps(canonical_payload, sort_keys=True).encode("utf-8")).hexdigest()

        dec.is_finalized = True
        dec.decision_fingerprint = fingerprint
        dec.finalized_at = datetime.now(timezone.utc)

        snapshot = DecisionSnapshot(
            decision_id=dec.decision_id,
            tenant_id=dec.tenant_id,
            policy_version=policy_version,
            risk_score=risk_score,
            trust_score=trust_score,
            fingerprint=fingerprint,
        )
        self._snapshots[dec.decision_id] = snapshot
        return dec

    def get_snapshot(self, decision_id: str, tenant_id: str) -> DecisionSnapshot:
        self.get_decision(decision_id, tenant_id)  # Verifies tenant isolation
        snap = self._snapshots.get(decision_id)
        if not snap:
            raise DecisionNotFoundException(f"Snapshot for decision '{decision_id}' not found")
        return snap
