"""Immutable Architecture Decision Records (ADRs) Subsystem."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from app.architecture_platform.exceptions import (
    ArchitectureDecisionException,
    CrossTenantArchitectureAccessException,
    ImmutableArchitectureDecisionException,
)


class ArchitectureDecisionStatus(str, Enum):
    DRAFT = "DRAFT"
    PROPOSED = "PROPOSED"
    APPROVED = "APPROVED"
    FINALIZED = "FINALIZED"
    REJECTED = "REJECTED"
    SUPERSEDED = "SUPERSEDED"


class ArchitectureDecisionOption(BaseModel):
    option_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    pros: List[str] = Field(default_factory=list)
    cons: List[str] = Field(default_factory=list)


class ArchitectureDecisionRecord(BaseModel):
    """Immutable ADR representation once finalized."""

    decision_id: str = Field(default_factory=lambda: f"adr_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    title: str
    status: ArchitectureDecisionStatus = ArchitectureDecisionStatus.DRAFT
    context: str
    options_considered: List[ArchitectureDecisionOption] = Field(default_factory=list)
    selected_option_id: Optional[str] = None
    rejected_alternatives_rationale: str = ""
    evidence_references: List[str] = Field(default_factory=list)
    impact_reference: Optional[str] = None
    risk_assessment_summary: str = "LOW"
    policy_version: str = "1.0.0"
    architecture_snapshot_reference: Optional[str] = None
    created_by: str = "system"
    superseded_by_decision_id: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    finalized_at: Optional[datetime] = None


ArchitectureDecision = ArchitectureDecisionRecord


class ArchitectureDecisionManager:
    """Manages creation, immutability, and superseding of Architecture Decision Records."""

    def __init__(self) -> None:
        self._decisions: Dict[str, ArchitectureDecisionRecord] = {}  # decision_id -> ADR

    def create_adr(
        self,
        tenant_id: str,
        title: str,
        context: str,
        options: List[ArchitectureDecisionOption],
        created_by: str = "system",
    ) -> ArchitectureDecisionRecord:
        adr = ArchitectureDecisionRecord(
            tenant_id=tenant_id,
            title=title,
            context=context,
            options_considered=options,
            created_by=created_by,
        )
        self._decisions[adr.decision_id] = adr
        return adr

    def update_draft_adr(
        self,
        decision_id: str,
        tenant_id: str,
        title: Optional[str] = None,
        context: Optional[str] = None,
        selected_option_id: Optional[str] = None,
    ) -> ArchitectureDecisionRecord:
        adr = self.get_adr(decision_id, tenant_id)
        if adr.status in (ArchitectureDecisionStatus.FINALIZED, ArchitectureDecisionStatus.APPROVED, ArchitectureDecisionStatus.REJECTED, ArchitectureDecisionStatus.SUPERSEDED):
            raise ImmutableArchitectureDecisionException(decision_id=decision_id, tenant_id=tenant_id)

        if title:
            adr.title = title
        if context:
            adr.context = context
        if selected_option_id:
            adr.selected_option_id = selected_option_id

        return adr

    def finalize_adr(
        self,
        decision_id: str,
        tenant_id: str,
        selected_option_id: str,
        rationale: str,
        snapshot_ref: Optional[str] = None,
    ) -> ArchitectureDecisionRecord:
        adr = self.get_adr(decision_id, tenant_id)
        if adr.status == ArchitectureDecisionStatus.FINALIZED:
            raise ImmutableArchitectureDecisionException(decision_id=decision_id, tenant_id=tenant_id)

        adr.selected_option_id = selected_option_id
        adr.rejected_alternatives_rationale = rationale
        adr.architecture_snapshot_reference = snapshot_ref
        adr.status = ArchitectureDecisionStatus.FINALIZED
        adr.finalized_at = datetime.now(timezone.utc)
        return adr

    def supersede_adr(self, old_decision_id: str, new_decision_id: str, tenant_id: str) -> ArchitectureDecisionRecord:
        old_adr = self.get_adr(old_decision_id, tenant_id)
        # Marking as superseded without mutating historical finalized rationale
        old_adr.status = ArchitectureDecisionStatus.SUPERSEDED
        old_adr.superseded_by_decision_id = new_decision_id
        return old_adr

    def get_adr(self, decision_id: str, tenant_id: str) -> ArchitectureDecisionRecord:
        adr = self._decisions.get(decision_id)
        if not adr:
            raise ArchitectureDecisionException(f"ADR '{decision_id}' not found.", tenant_id=tenant_id)
        if adr.tenant_id != tenant_id and tenant_id != "system":
            raise CrossTenantArchitectureAccessException(request_tenant=tenant_id, target_tenant=adr.tenant_id, resource_id=decision_id)
        return adr
