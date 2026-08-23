"""Immutable Enterprise Decision Lifecycle Subsystem."""

import hashlib
import json
from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.decision_intelligence.exceptions import (
    DecisionNotFoundException,
    ImmutableDecisionException,
    CrossTenantDecisionAccessException,
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


class DecisionStatus(str, Enum):
    DRAFT = "DRAFT"
    CONTEXT_ASSEMBLING = "CONTEXT_ASSEMBLING"
    EVIDENCE_COLLECTING = "EVIDENCE_COLLECTING"
    SCENARIO_ANALYSIS = "SCENARIO_ANALYSIS"
    CONSTRAINT_EVALUATION = "CONSTRAINT_EVALUATION"
    RISK_EVALUATION = "RISK_EVALUATION"
    TRUST_EVALUATION = "TRUST_EVALUATION"
    RECOMMENDATION_GENERATED = "RECOMMENDATION_GENERATED"
    GOVERNANCE_EVALUATION = "GOVERNANCE_EVALUATION"
    REQUIRES_APPROVAL = "REQUIRES_APPROVAL"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    DELEGATED = "DELEGATED"
    OUTCOME_MONITORING = "OUTCOME_MONITORING"
    FINALIZED = "FINALIZED"


class EnterpriseDecision(BaseModel):
    decision_id: str = Field(default_factory=lambda: f"dec_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    title: str
    decision_type: DecisionType = DecisionType.CROSS_DOMAIN
    status: DecisionStatus = DecisionStatus.DRAFT
    context_id: Optional[str] = None
    evidence_id: Optional[str] = None
    recommendation_id: Optional[str] = None
    governance_id: Optional[str] = None
    is_finalized: bool = False
    decision_fingerprint: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    finalized_at: Optional[datetime] = None


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

    def create_decision(self, tenant_id: str, title: str, decision_type: DecisionType = DecisionType.CROSS_DOMAIN) -> EnterpriseDecision:
        dec = EnterpriseDecision(tenant_id=tenant_id, title=title, decision_type=decision_type)
        self._decisions[dec.decision_id] = dec
        return dec

    def get_decision(self, decision_id: str, tenant_id: str) -> EnterpriseDecision:
        dec = self._decisions.get(decision_id)
        if not dec:
            raise DecisionNotFoundException(decision_id, tenant_id)
        if dec.tenant_id != tenant_id and tenant_id != "global":
            raise CrossTenantDecisionAccessException(tenant_id, dec.tenant_id)
        return dec

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
            raise ImmutableDecisionException(decision_id)

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
        dec.status = DecisionStatus.FINALIZED
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
            raise DecisionNotFoundException(decision_id, tenant_id)
        return snap
