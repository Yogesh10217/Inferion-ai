"""Cross-Platform Access Correlation (Phase 5.39)."""

from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.access_intelligence.exceptions import CrossTenantAccessIntelligenceException


class AccessCorrelationType(str, Enum):
    SECURITY_INCIDENT_ACCESS = "SECURITY_INCIDENT_ACCESS"
    AGENT_EXECUTION_ACCESS = "AGENT_EXECUTION_ACCESS"
    LIFECYCLE_RELEASE_ACCESS = "LIFECYCLE_RELEASE_ACCESS"
    EVENT_INTELLIGENCE_ACCESS = "EVENT_INTELLIGENCE_ACCESS"
    CONTROL_VIOLATION_ACCESS = "CONTROL_VIOLATION_ACCESS"


class AccessCorrelationConfidence(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class AccessCorrelationEvidence(BaseModel):
    """Evidence linking correlated events."""
    evidence_id: str = Field(default_factory=lambda: f"corr_evid_{uuid.uuid4().hex[:8]}")
    correlated_resource_ids: List[str] = Field(default_factory=list)
    correlation_reason: str = ""


class AccessCorrelation(BaseModel):
    """Access Correlation Representation."""
    correlation_id: str = Field(default_factory=lambda: f"corr_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    correlation_type: AccessCorrelationType
    confidence: AccessCorrelationConfidence = AccessCorrelationConfidence.HIGH
    subject_identity_id: str
    external_entity_id: str
    description: str
    evidence: AccessCorrelationEvidence
    correlated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AccessCorrelationManager:
    """Correlates access events across platform subsystems."""

    def __init__(self) -> None:
        self._correlations: Dict[str, AccessCorrelation] = {}

    def correlate_event(
        self,
        tenant_id: str,
        correlation_type: AccessCorrelationType,
        subject_identity_id: str,
        external_entity_id: str,
        description: str,
        correlated_resource_ids: List[str],
        confidence: AccessCorrelationConfidence = AccessCorrelationConfidence.HIGH,
    ) -> AccessCorrelation:
        evid = AccessCorrelationEvidence(
            correlated_resource_ids=correlated_resource_ids,
            correlation_reason=description,
        )
        corr = AccessCorrelation(
            tenant_id=tenant_id,
            correlation_type=correlation_type,
            confidence=confidence,
            subject_identity_id=subject_identity_id,
            external_entity_id=external_entity_id,
            description=description,
            evidence=evid,
        )
        self._correlations[corr.correlation_id] = corr
        return corr

    def get_correlation(self, tenant_id: str, correlation_id: str) -> AccessCorrelation:
        corr = self._correlations.get(correlation_id)
        if not corr or corr.tenant_id != tenant_id:
            raise CrossTenantAccessIntelligenceException()
        return corr

    def list_correlations(self, tenant_id: str, correlation_type: Optional[AccessCorrelationType] = None) -> List[AccessCorrelation]:
        results = [c for c in self._correlations.values() if c.tenant_id == tenant_id]
        if correlation_type:
            results = [c for c in results if c.correlation_type == correlation_type]
        return results
