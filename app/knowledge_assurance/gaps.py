"""Knowledge gap analysis intelligence for identifying missing context and documentation."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List

from pydantic import BaseModel, Field


class KnowledgeGapType(str, Enum):
    MISSING_DOCUMENTATION = "MISSING_DOCUMENTATION"
    MISSING_EVIDENCE = "MISSING_EVIDENCE"
    MISSING_PROCEDURES = "MISSING_PROCEDURES"
    MISSING_INCIDENT_KNOWLEDGE = "MISSING_INCIDENT_KNOWLEDGE"
    MISSING_DECISION_CONTEXT = "MISSING_DECISION_CONTEXT"
    MISSING_PROVENANCE = "MISSING_PROVENANCE"


class GapSeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class GapImpact(BaseModel):
    affected_domain: str
    impact_score: float = 0.5
    description: str = ""


class KnowledgeGapRecommendation(BaseModel):
    title: str
    action_item: str
    priority: str = "MEDIUM"


class KnowledgeGap(BaseModel):
    gap_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    gap_type: KnowledgeGapType
    severity: GapSeverity = GapSeverity.MEDIUM
    title: str
    description: str
    impact: GapImpact
    recommendation: KnowledgeGapRecommendation
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class KnowledgeGapManager:
    """Identifies knowledge gaps across enterprise domains."""

    def __init__(self) -> None:
        self._gaps: Dict[str, KnowledgeGap] = {}

    def create_gap(
        self,
        tenant_id: str,
        gap_type: KnowledgeGapType,
        title: str,
        description: str,
        severity: GapSeverity = GapSeverity.MEDIUM,
        impact_domain: str = "operations",
        action_item: str = "Create missing documentation",
    ) -> KnowledgeGap:
        gap = KnowledgeGap(
            tenant_id=tenant_id,
            gap_type=gap_type,
            title=title,
            description=description,
            severity=severity,
            impact=GapImpact(affected_domain=impact_domain, impact_score=0.7 if severity == GapSeverity.HIGH else 0.4),
            recommendation=KnowledgeGapRecommendation(
                title=f"Address {gap_type.value}",
                action_item=action_item,
                priority=severity.value,
            ),
        )
        self._gaps[gap.gap_id] = gap
        return gap

    def analyze_domain_gaps(
        self,
        tenant_id: str,
        domain: str = "GLOBAL",
    ) -> List[KnowledgeGap]:
        self.create_gap(
            tenant_id=tenant_id,
            gap_type=KnowledgeGapType.MISSING_DOCUMENTATION,
            title=f"Missing SOP for {domain}",
            description=f"No authoritative operational procedure found for domain '{domain}'.",
            severity=GapSeverity.HIGH,
            impact_domain=domain,
            action_item=f"Author missing SOP for {domain}.",
        )
        return self.list_gaps(tenant_id)

    def list_gaps(self, tenant_id: str) -> List[KnowledgeGap]:
        return [g for g in self._gaps.values() if g.tenant_id == tenant_id]
