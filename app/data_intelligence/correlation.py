"""Cross-platform data correlation (Phase 5.43)."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class CorrelationType(str, Enum):
    DATA_ANOMALY_TO_PIPELINE_FAILURE = "DATA_ANOMALY_TO_PIPELINE_FAILURE"
    DATA_ANOMALY_TO_SECURITY_INCIDENT = "DATA_ANOMALY_TO_SECURITY_INCIDENT"
    DATA_DRIFT_TO_MODEL_PERFORMANCE = "DATA_DRIFT_TO_MODEL_PERFORMANCE"
    DATA_STALENESS_TO_AGENT_FAILURE = "DATA_STALENESS_TO_AGENT_FAILURE"
    DATA_QUALITY_TO_KNOWLEDGE_INCONSISTENCY = "DATA_QUALITY_TO_KNOWLEDGE_INCONSISTENCY"
    SCHEMA_CHANGE_TO_CONTROL_VIOLATION = "SCHEMA_CHANGE_TO_CONTROL_VIOLATION"


class CorrelationEvidence(BaseModel):
    source_event_id: str
    target_event_id: str
    confidence: float
    description: str


class DataCorrelation(BaseModel):
    correlation_id: str
    tenant_id: str
    correlation_type: CorrelationType
    primary_resource_id: str
    correlated_resource_id: str
    confidence_score: float
    evidence: CorrelationEvidence
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DataCorrelationManager:
    """Correlates data intelligence signals with security, operational, and AI platform signals."""

    def __init__(self) -> None:
        self._correlations: Dict[str, DataCorrelation] = {}

    def correlate(
        self,
        tenant_id: str,
        correlation_type: CorrelationType,
        primary_resource_id: str,
        correlated_resource_id: str,
        confidence_score: float = 0.90,
        description: str = "",
        correlation_id: Optional[str] = None,
    ) -> DataCorrelation:
        cid = correlation_id or f"corr-{uuid.uuid4().hex[:8]}"

        ev = CorrelationEvidence(
            source_event_id=primary_resource_id,
            target_event_id=correlated_resource_id,
            confidence=confidence_score,
            description=description
            or f"Correlated {primary_resource_id} with {correlated_resource_id} ({correlation_type.value})",
        )

        corr = DataCorrelation(
            correlation_id=cid,
            tenant_id=tenant_id,
            correlation_type=correlation_type,
            primary_resource_id=primary_resource_id,
            correlated_resource_id=correlated_resource_id,
            confidence_score=confidence_score,
            evidence=ev,
        )
        self._correlations[cid] = corr
        return corr

    def list_correlations(self, tenant_id: str, primary_resource_id: Optional[str] = None) -> List[DataCorrelation]:
        corrs = [c for c in self._correlations.values() if c.tenant_id == tenant_id]
        if primary_resource_id:
            corrs = [c for c in corrs if c.primary_resource_id == primary_resource_id]
        return corrs
