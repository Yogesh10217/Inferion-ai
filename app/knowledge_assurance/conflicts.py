"""Knowledge conflict detection and resolution intelligence."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.knowledge_assurance.exceptions import (
    CrossTenantKnowledgeAssuranceException,
    KnowledgeConflictNotFoundException,
)


class KnowledgeConflictType(str, Enum):
    FACT = "FACT"
    FACT_CONFLICT = "FACT_CONFLICT"
    POLICY = "POLICY"
    POLICY_CONFLICT = "POLICY_CONFLICT"
    CONTEXT = "CONTEXT"
    RECOMMENDATION = "RECOMMENDATION"
    OUTDATED = "OUTDATED"
    EVIDENCE = "EVIDENCE"


class ConflictSeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ConflictStatus(str, Enum):
    OPEN = "OPEN"
    TRIAGED = "TRIAGED"
    RESOLVING = "RESOLVING"
    RESOLVED = "RESOLVED"
    DISMISSED = "DISMISSED"


class ConflictEvidence(BaseModel):
    source_a_id: str
    source_b_id: str
    statement_a: str
    statement_b: str
    description: str


class KnowledgeConflict(BaseModel):
    conflict_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    conflict_type: KnowledgeConflictType
    severity: ConflictSeverity = ConflictSeverity.MEDIUM
    status: ConflictStatus = ConflictStatus.OPEN
    title: str
    description: str
    evidence: List[ConflictEvidence] = Field(default_factory=list)
    requires_approval: bool = False
    resolution_summary: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class KnowledgeConflictManager:
    """Detects and coordinates resolution for knowledge conflicts."""

    def __init__(self) -> None:
        self._conflicts: Dict[str, KnowledgeConflict] = {}

    def create_conflict(
        self,
        tenant_id: str,
        conflict_type: Any,
        title: str = "Knowledge Conflict",
        description: str = "",
        severity: Any = ConflictSeverity.MEDIUM,
        evidence: Optional[List[ConflictEvidence]] = None,
        target_resource_id: Optional[str] = None,
        competing_sources: Optional[List[str]] = None,
    ) -> KnowledgeConflict:
        if isinstance(conflict_type, str):
            try:
                ctype = KnowledgeConflictType(conflict_type)
            except ValueError:
                ctype = KnowledgeConflictType.FACT
        else:
            ctype = conflict_type

        if isinstance(severity, str):
            try:
                sev = ConflictSeverity(severity)
            except ValueError:
                sev = ConflictSeverity.MEDIUM
        else:
            sev = severity

        if competing_sources and not description:
            description = f"Conflict detected across competing sources: {', '.join(competing_sources)}"

        requires_approval = sev in [ConflictSeverity.HIGH, ConflictSeverity.CRITICAL]
        conflict = KnowledgeConflict(
            tenant_id=tenant_id,
            conflict_type=ctype,
            title=title,
            description=description,
            severity=sev,
            status=ConflictStatus.OPEN,
            evidence=evidence or [],
            requires_approval=requires_approval,
        )
        self._conflicts[conflict.conflict_id] = conflict
        return conflict

    def register_conflict(
        self,
        tenant_id: str,
        conflict_type: Any,
        severity: Any = ConflictSeverity.MEDIUM,
        target_resource_id: Optional[str] = None,
        competing_sources: Optional[List[str]] = None,
        title: str = "Registered Conflict",
        description: str = "",
    ) -> KnowledgeConflict:
        return self.create_conflict(
            tenant_id=tenant_id,
            conflict_type=conflict_type,
            title=title,
            description=description,
            severity=severity,
            target_resource_id=target_resource_id,
            competing_sources=competing_sources,
        )

    def get_conflict(self, conflict_id: str, tenant_id: str) -> KnowledgeConflict:
        c = self._conflicts.get(conflict_id)
        if not c:
            raise KnowledgeConflictNotFoundException(f"Conflict '{conflict_id}' not found")
        if c.tenant_id != tenant_id:
            raise CrossTenantKnowledgeAssuranceException()
        return c

    def list_conflicts(self, tenant_id: str) -> List[KnowledgeConflict]:
        return [c for c in self._conflicts.values() if c.tenant_id == tenant_id]
