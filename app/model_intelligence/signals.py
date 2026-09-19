"""Sanitized Signal Intelligence for Model Intelligence (Phase 5.44)."""

import logging
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.platform_contracts.redaction import SensitiveDataSanitizer

logger = logging.getLogger(__name__)


class ModelSignalType(str, Enum):
    PERFORMANCE_SIGNAL = "PERFORMANCE_SIGNAL"
    SAFETY_SIGNAL = "SAFETY_SIGNAL"
    SECURITY_SIGNAL = "SECURITY_SIGNAL"
    COST_SIGNAL = "COST_SIGNAL"
    DRIFT_SIGNAL = "DRIFT_SIGNAL"


class ModelSignalSource(BaseModel):
    source_id: str
    source_name: str  # ai_lifecycle_platform, security_intelligence, reliability_platform, event_intelligence, operations_intelligence, data_intelligence
    environment: str = "production"


class ModelSignal(BaseModel):
    signal_id: str
    model_id: str
    tenant_id: str
    signal_type: ModelSignalType
    source: ModelSignalSource
    payload: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ModelSignalManager:
    """Manages model intelligence signals enforcing strict data sanitization."""

    def __init__(self) -> None:
        self.sanitizer = SensitiveDataSanitizer()
        self._signals: Dict[str, ModelSignal] = {}

    def ingest_signal(
        self,
        model_id: str,
        tenant_id: str,
        signal_type: ModelSignalType,
        source: ModelSignalSource,
        raw_payload: Dict[str, Any],
    ) -> ModelSignal:
        s_id = f"msig-{uuid.uuid4().hex[:8]}"

        # Sanitize payload to strip secrets, tokens, credentials, prompts
        sanitized_payload = self.sanitizer.sanitize(raw_payload)

        signal = ModelSignal(
            signal_id=s_id,
            model_id=model_id,
            tenant_id=tenant_id,
            signal_type=signal_type,
            source=source,
            payload=sanitized_payload,
        )

        self._signals[s_id] = signal
        logger.info(
            f"[MODEL SIGNAL] Ingested signal {s_id} for model {model_id} (Tenant: {tenant_id}) Source: {source.source_name}"
        )
        return signal

    def list_signals(self, tenant_id: str, model_id: Optional[str] = None) -> List[ModelSignal]:
        res = [s for s in self._signals.values() if s.tenant_id == tenant_id]
        if model_id:
            res = [s for s in res if s.model_id == model_id]
        return res
