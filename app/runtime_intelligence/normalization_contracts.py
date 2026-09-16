"""Standardized Normalization Contracts for Phase 5.57 Runtime Intelligence."""

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict

from app.platform_contracts.redaction import SensitiveDataSanitizer
from app.runtime_intelligence.models import NormalizedRuntimeSignal


class RuntimeSignalCategory(str, Enum):
    LATENCY = "LATENCY"
    ERROR = "ERROR"
    TIMEOUT = "TIMEOUT"
    RESOURCE = "RESOURCE"
    MEMORY = "MEMORY"
    CPU = "CPU"
    QUEUE = "QUEUE"
    DEPENDENCY = "DEPENDENCY"
    NETWORK = "NETWORK"
    DATABASE = "DATABASE"
    MODEL = "MODEL"
    INFERENCE = "INFERENCE"
    SECURITY = "SECURITY"
    IDENTITY = "IDENTITY"
    POLICY = "POLICY"
    DEPLOYMENT = "DEPLOYMENT"
    CONFIGURATION = "CONFIGURATION"


@dataclass
class RuntimeDomainInput:
    tenant_id: str
    source_domain: str
    signal_type: str
    raw_payload: Dict[str, Any]
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class RuntimeSignalNormalizerEngine:
    """Sanitizes, normalizes, and computes SHA-256 fingerprints for provider signals."""

    @classmethod
    def normalize_input(cls, domain_input: RuntimeDomainInput) -> NormalizedRuntimeSignal:
        sanitized = SensitiveDataSanitizer.sanitize(domain_input.raw_payload)

        fingerprint_data = {
            "tenant_id": domain_input.tenant_id,
            "source_domain": domain_input.source_domain,
            "signal_type": domain_input.signal_type,
            "sanitized": sanitized,
        }
        fingerprint = hashlib.sha256(json.dumps(fingerprint_data, sort_keys=True, default=str).encode()).hexdigest()
        sig_id = f"sig_{fingerprint[:12]}"

        return NormalizedRuntimeSignal(
            tenant_id=domain_input.tenant_id,
            signal_id=sig_id,
            normalized_type=domain_input.signal_type,
            normalized_severity=str(sanitized.get("severity", "MEDIUM")),
            source_domain=domain_input.source_domain,
            raw_payload=sanitized,
            fingerprint=fingerprint,
            timestamp=domain_input.timestamp,
        )
