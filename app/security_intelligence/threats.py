"""Threat Intelligence Subsystem (Phase 5.32)."""

from enum import Enum
from typing import Dict, Optional, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.security_intelligence.exceptions import SecurityThreatNotFoundException, CrossTenantSecurityAccessException


class ThreatType(str, Enum):
    IDENTITY_THREAT = "IDENTITY_THREAT"
    APPLICATION_THREAT = "APPLICATION_THREAT"
    API_THREAT = "API_THREAT"
    DATA_THREAT = "DATA_THREAT"
    INFRASTRUCTURE_THREAT = "INFRASTRUCTURE_THREAT"
    AI_MODEL_THREAT = "AI_MODEL_THREAT"
    AGENT_THREAT = "AGENT_THREAT"
    INTEGRATION_THREAT = "INTEGRATION_THREAT"
    SUPPLY_CHAIN_THREAT = "SUPPLY_CHAIN_THREAT"
    INSIDER_THREAT = "INSIDER_THREAT"


class ThreatSeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ThreatStatus(str, Enum):
    SUSPECTED = "SUSPECTED"
    CONFIRMED = "CONFIRMED"
    MITIGATED = "MITIGATED"
    FALSE_POSITIVE = "FALSE_POSITIVE"


class ThreatConfidence(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CERTAIN = "CERTAIN"


class ThreatEvidence(BaseModel):
    evidence_id: str
    signal_ids: List[str] = Field(default_factory=list)
    description: str


class SecurityThreat(BaseModel):
    threat_id: str = Field(default_factory=lambda: f"thrt_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    asset_id: str
    threat_type: ThreatType
    severity: ThreatSeverity = ThreatSeverity.MEDIUM
    status: ThreatStatus = ThreatStatus.SUSPECTED
    confidence: ThreatConfidence = ThreatConfidence.MEDIUM
    evidence_references: List[str] = Field(default_factory=list)
    detected_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ThreatManager:
    """Manages threat detection and references evidence without copying raw telemetry."""

    def __init__(self) -> None:
        self._threats: Dict[str, SecurityThreat] = {}

    def create_threat(
        self,
        tenant_id: str,
        asset_id: str,
        threat_type: ThreatType,
        severity: ThreatSeverity = ThreatSeverity.MEDIUM,
        confidence: ThreatConfidence = ThreatConfidence.MEDIUM,
        evidence_references: Optional[List[str]] = None,
    ) -> SecurityThreat:
        thrt = SecurityThreat(
            tenant_id=tenant_id,
            asset_id=asset_id,
            threat_type=threat_type,
            severity=severity,
            confidence=confidence,
            evidence_references=evidence_references or [],
        )
        self._threats[thrt.threat_id] = thrt
        return thrt

    def get_threat(self, threat_id: str, tenant_id: str) -> SecurityThreat:
        thrt = self._threats.get(threat_id)
        if not thrt:
            raise SecurityThreatNotFoundException(threat_id)
        if tenant_id != "global" and thrt.tenant_id != "global" and tenant_id != thrt.tenant_id:
            raise CrossTenantSecurityAccessException(tenant_id, thrt.tenant_id)
        return thrt

    def list_threats(self, tenant_id: str) -> List[SecurityThreat]:
        return [t for t in self._threats.values() if t.tenant_id == tenant_id]
