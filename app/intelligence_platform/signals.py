"""Intelligence Signal Fabric & Sanitized Telemetry Ingestion."""

import logging
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.intelligence_platform.exceptions import SignalValidationException
from app.security.secrets import SecretManager

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class SignalSource(str, Enum):
    OPERATIONS = "OPERATIONS"
    SECURITY = "SECURITY"
    GOVERNANCE = "GOVERNANCE"
    IDENTITY = "IDENTITY"
    FINOPS = "FINOPS"
    MLOPS = "MLOPS"
    APPLICATION = "APPLICATION"
    DEVELOPER = "DEVELOPER"
    WORKFLOW = "WORKFLOW"
    AGENT = "AGENT"
    KNOWLEDGE = "KNOWLEDGE"
    DATA_FABRIC = "DATA_FABRIC"
    INTEGRATION = "INTEGRATION"
    USER_FEEDBACK = "USER_FEEDBACK"


class SignalType(str, Enum):
    METRIC_THRESHOLD = "METRIC_THRESHOLD"
    LOG_ANOMALY = "LOG_ANOMALY"
    COST_SPIKE = "COST_SPIKE"
    PERFORMANCE_DEGRADATION = "PERFORMANCE_DEGRADATION"
    SECURITY_ALERT = "SECURITY_ALERT"
    POLICY_BREACH = "POLICY_BREACH"
    MODEL_DRIFT = "MODEL_DRIFT"
    FEEDBACK_DISCONTENT = "FEEDBACK_DISCONTENT"
    WORKFLOW_FAILURE = "WORKFLOW_FAILURE"
    DEPLOYMENT_EVENT = "DEPLOYMENT_EVENT"
    CAPACITY_WARNING = "CAPACITY_WARNING"


class SignalClassification(str, Enum):
    INFORMATIONAL = "INFORMATIONAL"
    OBSERVATION = "OBSERVATION"
    WARNING = "WARNING"
    CRITICAL_ALERT = "CRITICAL_ALERT"


class SignalConfidence(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    VERIFIED = "VERIFIED"


class SignalFreshness(BaseModel):
    ingested_at: datetime = Field(default_factory=_now)
    observed_at: datetime = Field(default_factory=_now)
    age_seconds: float = 0.0
    is_fresh: bool = True


class SignalCorrelation(BaseModel):
    correlation_id: str = Field(default_factory=lambda: f"corr_{uuid.uuid4().hex[:10]}")
    trace_id: Optional[str] = None
    span_id: Optional[str] = None
    related_signal_ids: List[str] = Field(default_factory=list)


class IntelligenceSignal(BaseModel):
    signal_id: str = Field(default_factory=lambda: f"sig_{uuid.uuid4().hex[:10]}")
    tenant_id: str = "global"
    source: SignalSource
    signal_type: SignalType
    classification: SignalClassification = SignalClassification.OBSERVATION
    confidence: SignalConfidence = SignalConfidence.HIGH
    message: str
    metrics: Dict[str, float] = Field(default_factory=dict)
    payload: Dict[str, Any] = Field(default_factory=dict)
    correlation: SignalCorrelation = Field(default_factory=SignalCorrelation)
    freshness: SignalFreshness = Field(default_factory=SignalFreshness)
    provenance_source: str = "system"
    resource_id: Optional[str] = None
    resource_type: Optional[str] = None


class SignalNormalizer:
    """Sanitizes raw secrets and normalizes telemetry signals."""

    def __init__(self, secret_manager: Optional[SecretManager] = None) -> None:
        self.secret_manager = secret_manager or SecretManager()

    def sanitize(self, text: str) -> str:
        if not text:
            return text
        return self.secret_manager.sanitize_text(text)

    def sanitize_payload(self, obj: Any) -> Any:
        if isinstance(obj, str):
            return self.sanitize(obj)
        elif isinstance(obj, dict):
            return {k: self.sanitize_payload(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self.sanitize_payload(item) for item in obj]
        return obj


class IntelligenceSignalManager:
    """Multi-tenant Intelligence Signal Fabric."""

    def __init__(self, secret_manager: Optional[SecretManager] = None) -> None:
        self.normalizer = SignalNormalizer(secret_manager=secret_manager)
        self._signals: Dict[str, IntelligenceSignal] = {}

    def ingest_signal(
        self,
        tenant_id: str,
        source: SignalSource,
        signal_type: SignalType,
        message: str,
        classification: SignalClassification = SignalClassification.OBSERVATION,
        confidence: SignalConfidence = SignalConfidence.HIGH,
        metrics: Optional[Dict[str, float]] = None,
        payload: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None,
        resource_id: Optional[str] = None,
        resource_type: Optional[str] = None,
    ) -> IntelligenceSignal:
        if not tenant_id:
            raise SignalValidationException("Tenant ID is required for signal ingestion.")

        sanitized_msg = self.normalizer.sanitize(message)
        sanitized_payload = self.normalizer.sanitize_payload(payload or {})

        corr = SignalCorrelation(correlation_id=correlation_id or f"corr_{uuid.uuid4().hex[:10]}")

        sig = IntelligenceSignal(
            tenant_id=tenant_id,
            source=source,
            signal_type=signal_type,
            classification=classification,
            confidence=confidence,
            message=sanitized_msg,
            metrics=metrics or {},
            payload=sanitized_payload,
            correlation=corr,
            freshness=SignalFreshness(),
            resource_id=resource_id,
            resource_type=resource_type,
        )

        self._signals[sig.signal_id] = sig
        logger.info(f"[INTELLIGENCE SIGNAL] Ingested {source.value}/{signal_type.value} signal '{sig.signal_id}' for tenant '{tenant_id}'")
        return sig

    def get_signal(self, signal_id: str, tenant_id: str) -> IntelligenceSignal:
        sig = self._signals.get(signal_id)
        if not sig or sig.tenant_id != tenant_id:
            raise SignalValidationException(f"Signal '{signal_id}' not found for tenant '{tenant_id}'.")
        return sig

    def list_signals(self, tenant_id: str, source: Optional[SignalSource] = None, resource_id: Optional[str] = None) -> List[IntelligenceSignal]:
        res = [s for s in self._signals.values() if s.tenant_id == tenant_id]
        if source:
            res = [s for s in res if s.source == source]
        if resource_id:
            res = [s for s in res if s.resource_id == resource_id]
        return res
