"""Security Signals Engine."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class SecuritySignalType(str, Enum):
    IOC_MATCH = "IOC_MATCH"
    PROMPT_INJECTION_ATTEMPT = "PROMPT_INJECTION_ATTEMPT"
    EXCESSIVE_PRIVILEGE_USAGE = "EXCESSIVE_PRIVILEGE_USAGE"
    UNUSUAL_EXFILTRATION_VOLUME = "UNUSUAL_EXFILTRATION_VOLUME"
    POLICY_VIOLATION = "POLICY_VIOLATION"


class SecuritySignal(BaseModel):
    signal_id: str = Field(default_factory=lambda: f"sec-sig-{uuid.uuid4().hex[:8]}")
    tenant_id: str
    signal_type: SecuritySignalType
    source_asset_id: str
    severity: str = "HIGH"
    payload: Dict[str, Any] = Field(default_factory=dict)
    emitted_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class SecuritySignalEngine:
    """Emits and indexes raw security observability signals across platform components."""

    def __init__(self) -> None:
        self._signals: Dict[str, SecuritySignal] = {}

    def emit_signal(
        self,
        tenant_id: str,
        signal_type: SecuritySignalType,
        source_asset_id: str,
        severity: str = "HIGH",
        payload: Optional[Dict[str, Any]] = None,
    ) -> SecuritySignal:
        sig = SecuritySignal(
            tenant_id=tenant_id,
            signal_type=signal_type,
            source_asset_id=source_asset_id,
            severity=severity,
            payload=payload or {},
        )
        self._signals[sig.signal_id] = sig
        return sig

    def list_signals(self, tenant_id: str) -> List[SecuritySignal]:
        return [s for s in self._signals.values() if s.tenant_id == tenant_id]
