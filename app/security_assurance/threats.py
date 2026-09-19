"""Threat Intelligence Data Models & Store."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.security_assurance.exceptions import CrossTenantSecurityAssuranceException, SecurityThreatNotFoundException


class ThreatSeverity(str, Enum):
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ThreatType(str, Enum):
    PROMPT_INJECTION = "PROMPT_INJECTION"
    MODEL_EXFILTRATION = "MODEL_EXFILTRATION"
    DATA_POISONING = "DATA_POISONING"
    UNAUTHORIZED_ACCESS = "UNAUTHORIZED_ACCESS"
    CREDENTIAL_EXPOSURE = "CREDENTIAL_EXPOSURE"
    PRIVILEGE_ESCALATION = "PRIVILEGE_ESCALATION"
    ANOMALOUS_API_TRAFFIC = "ANOMALOUS_API_TRAFFIC"
    MALICIOUS_DEPENDENCY = "MALICIOUS_DEPENDENCY"


class SecurityThreat(BaseModel):
    threat_id: str = Field(default_factory=lambda: f"threat-{uuid.uuid4().hex[:8]}")
    tenant_id: str
    title: str
    threat_type: ThreatType
    severity: ThreatSeverity
    target_asset_id: Optional[str] = None
    description: str = ""
    status: str = "ACTIVE"  # ACTIVE, MITIGATED, DISMISSED
    indicators: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    detected_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class SecurityThreatStore:
    """In-memory store for threat intelligence and recorded security threats."""

    def __init__(self) -> None:
        self._threats: Dict[str, SecurityThreat] = {}

    def record_threat(
        self,
        tenant_id: str,
        title: str,
        threat_type: ThreatType,
        severity: ThreatSeverity,
        target_asset_id: Optional[str] = None,
        description: str = "",
        indicators: Optional[List[str]] = None,
        metadata: Optional[Dict] = None,
    ) -> SecurityThreat:
        threat = SecurityThreat(
            tenant_id=tenant_id,
            title=title,
            threat_type=threat_type,
            severity=severity,
            target_asset_id=target_asset_id,
            description=description,
            indicators=indicators or [],
            metadata=metadata or {},
        )
        self._threats[threat.threat_id] = threat
        return threat

    def get_threat(self, tenant_id: str, threat_id: str) -> SecurityThreat:
        threat = self._threats.get(threat_id)
        if not threat:
            raise SecurityThreatNotFoundException(f"Threat '{threat_id}' not found.")
        if threat.tenant_id != tenant_id:
            raise CrossTenantSecurityAssuranceException(
                f"Tenant '{tenant_id}' cannot access threat for tenant '{threat.tenant_id}'."
            )
        return threat

    def list_threats(self, tenant_id: str, status: Optional[str] = None) -> List[SecurityThreat]:
        results = [t for t in self._threats.values() if t.tenant_id == tenant_id]
        if status:
            results = [t for t in results if t.status == status]
        return results
