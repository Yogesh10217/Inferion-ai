"""Standardized Normalization Contracts for Phase 5.57 Runtime Intelligence."""

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, Any, Optional

from app.platform_contracts.sanitizer import SensitiveDataSanitizer


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


@dataclass
class NormalizedRuntimeSignal:
    tenant_id: str
    signal_id: str
    source_domain: str
    category: RuntimeSignalCategory
    metric_name: str
    metric_value: float
    unit: str
    sanitized_metadata: Dict[str, Any]
    signal_fingerprint: str
    normalized_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class RuntimeSignalNormalizerEngine:
    """Sanitizes, normalizes, and computes SHA-256 fingerprints for provider signals."""

    @classmethod
    def normalize_input(cls, domain_input: RuntimeDomainInput) -> NormalizedRuntimeSignal:
        sanitized = SensitiveDataSanitizer.sanitize(domain_input.raw_payload)
        category_enum = RuntimeSignalCategory(domain_input.signal_type.upper()) if domain_input.signal_type.upper() in RuntimeSignalCategory.__members__ else RuntimeSignalCategory.RESOURCE
        
        sig_id = f"sig_{hashlib.sha256(f'{domain_input.tenant_id}:{domain_input.source_domain}:{domain_input.timestamp}'.encode()).hexdigest()[:12]}"
        
        fingerprint_data = {
            "tenant_id": domain_input.tenant_id,
            "source_domain": domain_input.source_domain,
            "signal_type": domain_input.signal_type,
            "sanitized": sanitized,
        }
        fingerprint = hashlib.sha256(json.dumps(fingerprint_data, sort_keys=True, default=str).encode()).hexdigest()

        return NormalizedRuntimeSignal(
            tenant_id=domain_input.tenant_id,
            signal_id=sig_id,
            source_domain=domain_input.source_domain,
            category=category_enum,
            metric_name=sanitized.get("metric_name", "runtime_metric"),
            metric_value=float(sanitized.get("value", 0.0)),
            unit=str(sanitized.get("unit", "units")),
            sanitized_metadata=sanitized,
            signal_fingerprint=fingerprint,
        )
