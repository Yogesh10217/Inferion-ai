"""Cross-Domain Identity Signals."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.platform_contracts.redaction import SensitiveDataSanitizer


class IdentitySignalType(str, Enum):
    AUTH_ANOMALY = "AUTH_ANOMALY"
    PRIVILEGE_CREEP = "PRIVILEGE_CREEP"
    ACCESS_VIOLATION = "ACCESS_VIOLATION"
    TOXIC_COMBINATION = "TOXIC_COMBINATION"
    POLICY_VIOLATION = "POLICY_VIOLATION"
    AGENT_BEHAVIOR_ANOMALY = "AGENT_BEHAVIOR_ANOMALY"


class IdentitySignalSource(str, Enum):
    ACCESS_INTELLIGENCE = "ACCESS_INTELLIGENCE"
    SECURITY_INTELLIGENCE = "SECURITY_INTELLIGENCE"
    OPERATIONS_INTELLIGENCE = "OPERATIONS_INTELLIGENCE"
    MODEL_INTELLIGENCE = "MODEL_INTELLIGENCE"
    AGENT_ORCHESTRATION = "AGENT_ORCHESTRATION"
    DECISION_GOVERNANCE = "DECISION_GOVERNANCE"
    POLICY_INTELLIGENCE = "POLICY_INTELLIGENCE"


class IdentitySignal(BaseModel):
    signal_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    identity_id: str
    signal_type: IdentitySignalType
    source: IdentitySignalSource
    severity: str = "MEDIUM"
    payload: Dict[str, Any] = Field(default_factory=dict)
    emitted_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class IdentitySignalManager:
    """Manages cross-domain identity signals with mandatory secret sanitization."""

    def __init__(self, sanitizer: Optional[SensitiveDataSanitizer] = None) -> None:
        self.sanitizer = sanitizer or SensitiveDataSanitizer()
        self._signals: Dict[str, IdentitySignal] = {}

    def emit_signal(
        self,
        tenant_id: str,
        identity_id: str,
        signal_type: IdentitySignalType,
        source: IdentitySignalSource,
        severity: str = "MEDIUM",
        payload: Optional[Dict[str, Any]] = None,
    ) -> IdentitySignal:
        sanitized_payload = self.sanitizer.sanitize(payload or {})
        signal = IdentitySignal(
            tenant_id=tenant_id,
            identity_id=identity_id,
            signal_type=signal_type,
            source=source,
            severity=severity,
            payload=sanitized_payload,
        )
        self._signals[signal.signal_id] = signal
        return signal

    def list_signals(
        self,
        tenant_id: str,
        identity_id: Optional[str] = None,
    ) -> List[IdentitySignal]:
        res = []
        for sig in self._signals.values():
            if sig.tenant_id == tenant_id:
                if identity_id is None or sig.identity_id == identity_id:
                    res.append(sig)
        return res
