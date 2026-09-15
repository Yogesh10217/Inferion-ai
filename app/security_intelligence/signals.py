"""Security Signal Processing Subsystem (Phase 5.32)."""

from enum import Enum
from typing import Dict, Any, Optional
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.platform_contracts.redaction import SensitiveDataSanitizer
from app.security_intelligence.exceptions import SecuritySignalValidationException


class SecuritySignalType(str, Enum):
    AUTHENTICATION_ANOMALY = "AUTHENTICATION_ANOMALY"
    AUTHORIZATION_FAILURE = "AUTHORIZATION_FAILURE"
    SECRET_EXPOSURE = "SECRET_EXPOSURE"
    SUSPICIOUS_API_ACTIVITY = "SUSPICIOUS_API_ACTIVITY"
    PROMPT_INJECTION_ATTEMPT = "PROMPT_INJECTION_ATTEMPT"
    DATA_EXFILTRATION_ATTEMPT = "DATA_EXFILTRATION_ATTEMPT"
    UNUSUAL_AGENT_BEHAVIOR = "UNUSUAL_AGENT_BEHAVIOR"
    MODEL_ABUSE = "MODEL_ABUSE"
    VULNERABILITY_DETECTED = "VULNERABILITY_DETECTED"
    MALICIOUS_TOOL_USAGE = "MALICIOUS_TOOL_USAGE"
    PRIVILEGE_ESCALATION = "PRIVILEGE_ESCALATION"
    ANOMALOUS_NETWORK_ACTIVITY = "ANOMALOUS_NETWORK_ACTIVITY"
    POLICY_VIOLATION = "POLICY_VIOLATION"


class SecuritySignalSeverity(str, Enum):
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class SecuritySignalSource(str, Enum):
    API_GATEWAY = "API_GATEWAY"
    IDENTITY_PROVIDER = "IDENTITY_PROVIDER"
    MODEL_GATEWAY = "MODEL_GATEWAY"
    AGENT_RUNTIME = "AGENT_RUNTIME"
    NETWORK_SENSOR = "NETWORK_SENSOR"
    VULNERABILITY_SCANNER = "VULNERABILITY_SCANNER"
    AUDIT_LOG = "AUDIT_LOG"


class SecuritySignal(BaseModel):
    signal_id: str = Field(default_factory=lambda: f"sig_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    asset_id: str
    signal_type: SecuritySignalType
    severity: SecuritySignalSeverity = SecuritySignalSeverity.MEDIUM
    source: SecuritySignalSource = SecuritySignalSource.API_GATEWAY
    payload: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class SecuritySignalManager:
    """Ingests and sanitizes operational security signals."""

    def __init__(self) -> None:
        self.sanitizer = SensitiveDataSanitizer()

    def ingest_signal(
        self,
        tenant_id: str,
        asset_id: str,
        signal_type: SecuritySignalType,
        severity: SecuritySignalSeverity = SecuritySignalSeverity.MEDIUM,
        source: SecuritySignalSource = SecuritySignalSource.API_GATEWAY,
        payload: Optional[Dict[str, Any]] = None,
    ) -> SecuritySignal:
        if not tenant_id or not asset_id:
            raise SecuritySignalValidationException("Both tenant_id and asset_id are required for security signals.")

        sanitized_payload = self.sanitizer.sanitize_copy(payload or {})
        return SecuritySignal(
            tenant_id=tenant_id,
            asset_id=asset_id,
            signal_type=signal_type,
            severity=severity,
            source=source,
            payload=sanitized_payload,
        )
