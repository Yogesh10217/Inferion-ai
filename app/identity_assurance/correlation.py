"""Cross-Domain Identity Correlation."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List

from pydantic import BaseModel, Field

from app.identity_assurance.exceptions import CrossTenantIdentityAssuranceException


class CorrelationType(str, Enum):
    IDENTITY_ACCESS_THREAT = "IDENTITY_ACCESS_THREAT"
    AGENT_MODEL_RISK = "AGENT_MODEL_RISK"
    PRIVILEGE_POLICY_VIOLATION = "PRIVILEGE_POLICY_VIOLATION"
    CROSS_DOMAIN_IDENTITY_THREAT = "CROSS_DOMAIN_IDENTITY_THREAT"


class CorrelationEvidence(BaseModel):
    source_domain: str
    evidence_description: str
    risk_score: float = 0.5


class IdentityCorrelation(BaseModel):
    correlation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    identity_id: str
    correlation_type: CorrelationType
    composite_risk_score: float = 0.8
    correlated_evidence: List[CorrelationEvidence] = Field(default_factory=list)
    correlated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class IdentityCorrelationManager:
    """Correlates identity risks across security, access, model, agent, and policy domains."""

    def __init__(self) -> None:
        self._correlations: Dict[str, IdentityCorrelation] = {}

    def correlate_identity_risk(
        self,
        tenant_id: str,
        identity_id: str,
        evidence_items: List[CorrelationEvidence],
    ) -> IdentityCorrelation:
        comp_risk = min(1.0, sum(e.risk_score for e in evidence_items) / max(1, len(evidence_items)) * 1.2)

        corr = IdentityCorrelation(
            tenant_id=tenant_id,
            identity_id=identity_id,
            correlation_type=CorrelationType.CROSS_DOMAIN_IDENTITY_THREAT,
            composite_risk_score=round(comp_risk, 4),
            correlated_evidence=evidence_items,
        )
        self._correlations[corr.correlation_id] = corr
        return corr

    def get_correlation(self, tenant_id: str, correlation_id: str) -> IdentityCorrelation:
        corr = self._correlations.get(correlation_id)
        if not corr or corr.tenant_id != tenant_id:
            raise CrossTenantIdentityAssuranceException()
        return corr
