"""Cross-Platform Event Correlation Subsystem (Phase 5.34)."""

from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.event_intelligence.events import EnterpriseEvent
from app.event_intelligence.exceptions import CrossTenantEventAccessException


class CorrelationType(str, Enum):
    TEMPORAL = "TEMPORAL"
    TOPOLOGICAL = "TOPOLOGICAL"
    CAUSAL = "CAUSAL"
    SECURITY_INCIDENT = "SECURITY_INCIDENT"
    RELIABILITY_CASCADE = "RELIABILITY_CASCADE"
    CROSS_DOMAIN = "CROSS_DOMAIN"


class CorrelationConfidence(BaseModel):
    score: float = 0.90


class CorrelationEvidence(BaseModel):
    evidence_id: str = Field(default_factory=lambda: f"evid_{uuid.uuid4().hex[:12]}")
    source_subsystem: str
    reference_id: str
    description: str


class CorrelationGroup(BaseModel):
    group_id: str = Field(default_factory=lambda: f"corr_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    title: str
    correlation_type: CorrelationType = CorrelationType.CROSS_DOMAIN
    event_ids: List[str] = Field(default_factory=list)
    evidences: List[CorrelationEvidence] = Field(default_factory=list)
    confidence: CorrelationConfidence = Field(default_factory=CorrelationConfidence)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class EventCorrelation(BaseModel):
    correlation_id: str
    group: CorrelationGroup


class EventCorrelationManager:
    """Correlates cross-platform enterprise events while maintaining tenant boundaries and evidence chains."""

    def __init__(self) -> None:
        self._groups: Dict[str, CorrelationGroup] = {}

    def correlate_events(
        self,
        tenant_id: str,
        title: str,
        events: List[EnterpriseEvent],
        correlation_type: CorrelationType = CorrelationType.CROSS_DOMAIN,
        evidences: Optional[List[CorrelationEvidence]] = None,
    ) -> CorrelationGroup:
        event_ids = []
        for e in events:
            if e.tenant_id != tenant_id:
                raise CrossTenantEventAccessException(tenant_id, e.tenant_id)
            event_ids.append(e.event_id)

        group = CorrelationGroup(
            tenant_id=tenant_id,
            title=title,
            correlation_type=correlation_type,
            event_ids=event_ids,
            evidences=evidences or [],
        )
        self._groups[group.group_id] = group

        for e in events:
            e.correlation_reference = group.group_id

        return group

    def get_group(self, group_id: str, tenant_id: str) -> CorrelationGroup:
        grp = self._groups.get(group_id)
        if not grp:
            raise KeyError(f"Correlation group '{group_id}' not found.")
        if tenant_id != "global" and grp.tenant_id != "global" and tenant_id != grp.tenant_id:
            raise CrossTenantEventAccessException(tenant_id, grp.tenant_id)
        return grp

    def list_groups(self, tenant_id: str) -> List[CorrelationGroup]:
        return [g for g in self._groups.values() if g.tenant_id == tenant_id]
