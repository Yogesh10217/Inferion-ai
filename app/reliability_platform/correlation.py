"""Cross-Service Incident Correlation Subsystem (Phase 5.31)."""

from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.platform_contracts.tenant import TenantIsolationValidator


class CorrelationStrategy(str, Enum):
    SERVICE_DEPENDENCY = "SERVICE_DEPENDENCY"
    TEMPORAL_PROXIMITY = "TEMPORAL_PROXIMITY"
    COMMON_INFRASTRUCTURE = "COMMON_INFRASTRUCTURE"
    ERROR_PATTERN = "ERROR_PATTERN"


class IncidentCorrelation(BaseModel):
    correlation_id: str = Field(default_factory=lambda: f"corr_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    primary_incident_id: str
    correlated_incident_ids: List[str] = Field(default_factory=list)
    strategy: CorrelationStrategy = CorrelationStrategy.SERVICE_DEPENDENCY
    confidence_score: float = 0.90
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CorrelationManager:
    """Correlates multiple cascading incidents into a unified incident context."""

    def __init__(self) -> None:
        self._correlations: Dict[str, IncidentCorrelation] = {}

    def correlate_incidents(
        self,
        tenant_id: str,
        primary_incident_id: str,
        correlated_incident_ids: List[str],
        strategy: CorrelationStrategy = CorrelationStrategy.SERVICE_DEPENDENCY,
    ) -> IncidentCorrelation:
        corr = IncidentCorrelation(
            tenant_id=tenant_id,
            primary_incident_id=primary_incident_id,
            correlated_incident_ids=correlated_incident_ids,
            strategy=strategy,
        )
        self._correlations[corr.correlation_id] = corr
        return corr
