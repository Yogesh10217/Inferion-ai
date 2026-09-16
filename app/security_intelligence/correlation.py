"""Cross-Domain Security Correlation Subsystem (Phase 5.32)."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from app.security_intelligence.exceptions import CrossTenantSecurityAccessException


class CorrelationType(str, Enum):
    SIGNAL_TO_THREAT = "SIGNAL_TO_THREAT"
    THREAT_TO_VULNERABILITY = "THREAT_TO_VULNERABILITY"
    THREAT_TO_RELIABILITY_INCIDENT = "THREAT_TO_RELIABILITY_INCIDENT"
    THREAT_TO_COMPLIANCE_FINDING = "THREAT_TO_COMPLIANCE_FINDING"
    THREAT_TO_DATA_GOVERNANCE = "THREAT_TO_DATA_GOVERNANCE"
    MULTI_STAGE_ATTACK_CHAIN = "MULTI_STAGE_ATTACK_CHAIN"


class CorrelationConfidence(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    VERY_HIGH = "VERY_HIGH"


class AttackChain(BaseModel):
    chain_id: str = Field(default_factory=lambda: f"chain_{uuid.uuid4().hex[:12]}")
    steps: List[str] = Field(default_factory=list)


class SecurityCorrelation(BaseModel):
    correlation_id: str = Field(default_factory=lambda: f"corr_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    correlation_type: CorrelationType
    confidence: CorrelationConfidence = CorrelationConfidence.HIGH
    primary_threat_id: str
    vulnerability_ids: List[str] = Field(default_factory=list)
    reliability_incident_ids: List[str] = Field(default_factory=list)
    compliance_finding_ids: List[str] = Field(default_factory=list)
    attack_chain: Optional[AttackChain] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class SecurityCorrelationManager:
    """Correlates security signals, threats, vulnerabilities, architecture dependencies, and incidents."""

    def __init__(self) -> None:
        self._correlations: Dict[str, SecurityCorrelation] = {}

    def correlate_security_event(
        self,
        tenant_id: str,
        primary_threat_id: str,
        vulnerability_ids: Optional[List[str]] = None,
        reliability_incident_ids: Optional[List[str]] = None,
        compliance_finding_ids: Optional[List[str]] = None,
        correlation_type: CorrelationType = CorrelationType.MULTI_STAGE_ATTACK_CHAIN,
    ) -> SecurityCorrelation:
        chain = AttackChain(steps=[primary_threat_id] + (vulnerability_ids or []))
        corr = SecurityCorrelation(
            tenant_id=tenant_id,
            correlation_type=correlation_type,
            primary_threat_id=primary_threat_id,
            vulnerability_ids=vulnerability_ids or [],
            reliability_incident_ids=reliability_incident_ids or [],
            compliance_finding_ids=compliance_finding_ids or [],
            attack_chain=chain,
        )
        self._correlations[corr.correlation_id] = corr
        return corr

    def get_correlation(self, correlation_id: str, tenant_id: str) -> SecurityCorrelation:
        corr = self._correlations.get(correlation_id)
        if not corr:
            raise KeyError(f"Correlation '{correlation_id}' not found.")
        if tenant_id != "global" and corr.tenant_id != "global" and tenant_id != corr.tenant_id:
            raise CrossTenantSecurityAccessException(tenant_id, corr.tenant_id)
        return corr
