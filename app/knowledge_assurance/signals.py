"""Knowledge signal ingestion using SensitiveDataSanitizer."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List

from pydantic import BaseModel, Field

from app.platform_contracts.redaction import SensitiveDataSanitizer


class KnowledgeSignalType(str, Enum):
    REFERENCE_CREATED = "REFERENCE_CREATED"
    CONFLICT_DETECTED = "CONFLICT_DETECTED"
    STALE_KNOWLEDGE = "STALE_KNOWLEDGE"
    TRUST_DEGRADATION = "TRUST_DEGRADATION"
    PROVENANCE_DISPUTE = "PROVENANCE_DISPUTE"
    GAP_IDENTIFIED = "GAP_IDENTIFIED"


class KnowledgeSignalSource(str, Enum):
    KNOWLEDGE_INTELLIGENCE = "KNOWLEDGE_INTELLIGENCE"
    DECISION_GOVERNANCE = "DECISION_GOVERNANCE"
    DATA_INTELLIGENCE = "DATA_INTELLIGENCE"
    MODEL_INTELLIGENCE = "MODEL_INTELLIGENCE"
    OPERATIONS_INTELLIGENCE = "OPERATIONS_INTELLIGENCE"
    CONTROL_ASSURANCE = "CONTROL_ASSURANCE"
    EVENT_INTELLIGENCE = "EVENT_INTELLIGENCE"
    SECURITY_INTELLIGENCE = "SECURITY_INTELLIGENCE"


class KnowledgeSignalSeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class KnowledgeSignal(BaseModel):
    signal_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    source_domain: KnowledgeSignalSource
    signal_type: KnowledgeSignalType
    severity: KnowledgeSignalSeverity = KnowledgeSignalSeverity.MEDIUM
    title: str
    description: str = ""
    sanitized_payload: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class KnowledgeSignalManager:
    """Ingests cross-platform telemetry signals for knowledge reasoning."""

    def __init__(self) -> None:
        self._signals: Dict[str, KnowledgeSignal] = {}

    def ingest_signal(
        self,
        tenant_id: str,
        source_domain: KnowledgeSignalSource,
        signal_type: KnowledgeSignalType,
        title: str,
        payload: Dict[str, Any],
        description: str = "",
        severity: KnowledgeSignalSeverity = KnowledgeSignalSeverity.MEDIUM,
    ) -> KnowledgeSignal:
        sanitized = SensitiveDataSanitizer.sanitize(payload)
        sig = KnowledgeSignal(
            tenant_id=tenant_id,
            source_domain=source_domain,
            signal_type=signal_type,
            severity=severity,
            title=title,
            description=description,
            sanitized_payload=sanitized,
        )
        self._signals[sig.signal_id] = sig
        return sig

    def list_signals(self, tenant_id: str) -> List[KnowledgeSignal]:
        return [s for s in self._signals.values() if s.tenant_id == tenant_id]
