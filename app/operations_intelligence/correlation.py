"""Cross-Platform Operational Event Correlation (Phase 5.41)."""

import uuid
from datetime import datetime, timezone
from typing import Dict, List

from pydantic import BaseModel, Field

from app.operations_intelligence.exceptions import CrossTenantOperationsAccessException


class CorrelationEvidence(BaseModel):
    evidence_id: str = Field(default_factory=lambda: f"ev_corr_{uuid.uuid4().hex[:8]}")
    event_source: str  # ALERTS, SECURITY, AGENT, INTEGRATION, RESILIENCE, DEPLOYMENT, CONTROL
    event_id: str
    summary: str


class OperationalCorrelation(BaseModel):
    correlation_id: str = Field(default_factory=lambda: f"corr_op_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    primary_incident_id: str
    correlated_events: List[CorrelationEvidence] = Field(default_factory=list)
    confidence_score: float = 85.0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CorrelationManager:
    """Correlates cross-platform signals into cohesive operational incident context."""

    def __init__(self) -> None:
        self._correlations: Dict[str, OperationalCorrelation] = {}

    def correlate_events(
        self,
        tenant_id: str,
        primary_incident_id: str,
        events: List[CorrelationEvidence],
        confidence_score: float = 85.0,
    ) -> OperationalCorrelation:
        corr = OperationalCorrelation(
            tenant_id=tenant_id,
            primary_incident_id=primary_incident_id,
            correlated_events=events,
            confidence_score=confidence_score,
        )
        self._correlations[corr.correlation_id] = corr
        return corr

    def get_correlation(self, tenant_id: str, correlation_id: str) -> OperationalCorrelation:
        corr = self._correlations.get(correlation_id)
        if not corr or corr.tenant_id != tenant_id:
            raise CrossTenantOperationsAccessException()
        return corr
