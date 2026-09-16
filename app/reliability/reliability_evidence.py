"""
Phase 5.70 - Reliability Evidence Module.

Collects, sanitizes, and SHA-256 fingerprints reliability evidence across all levels:
STATIC, UNIT_TEST, INTEGRATION_TEST, ASGI_RUNTIME, SIMULATION_RUNTIME, CONTAINER_RUNTIME, INFRASTRUCTURE_RUNTIME, PRODUCTION_RUNTIME.
"""

import hashlib
import json
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

from app.deployment.secrets import get_secrets_sanitizer


class ReliabilityEvidenceLevel(str, Enum):
    STATIC = "STATIC"
    UNIT_TEST = "UNIT_TEST"
    INTEGRATION_TEST = "INTEGRATION_TEST"
    ASGI_RUNTIME = "ASGI_RUNTIME"
    SIMULATION_RUNTIME = "SIMULATION_RUNTIME"
    CONTAINER_RUNTIME = "CONTAINER_RUNTIME"
    INFRASTRUCTURE_RUNTIME = "INFRASTRUCTURE_RUNTIME"
    PRODUCTION_RUNTIME = "PRODUCTION_RUNTIME"


@dataclass
class ReliabilityEvidence:
    timestamp: float
    component: str
    event: str
    status: str
    evidence_level: ReliabilityEvidenceLevel
    sanitized_payload: Dict[str, Any]
    fingerprint: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "component": self.component,
            "event": self.event,
            "status": self.status,
            "evidence_level": self.evidence_level.value,
            "sanitized_payload": self.sanitized_payload,
            "fingerprint": self.fingerprint,
        }


class ReliabilityEvidenceCollector:
    """Collects raw evidence, sanitizes secrets, converts to canonical deterministic JSON, and generates SHA256 fingerprints."""

    def __init__(self) -> None:
        self.sanitizer = get_secrets_sanitizer()
        self._evidence_records: List[ReliabilityEvidence] = []

    def collect_evidence(
        self,
        component: str,
        event: str,
        status: str,
        evidence_level: ReliabilityEvidenceLevel,
        raw_payload: Dict[str, Any],
        timestamp: Optional[float] = None,
    ) -> ReliabilityEvidence:
        if timestamp is None:
            timestamp = time.time()

        # Secret sanitization
        sanitized_payload = self.sanitizer.sanitize_dict(raw_payload)

        # Deterministic JSON representation for fingerprinting
        canonical_obj = {
            "component": component,
            "event": event,
            "evidence_level": evidence_level.value,
            "sanitized_payload": sanitized_payload,
            "status": status,
            "timestamp": timestamp,
        }
        deterministic_json = json.dumps(canonical_obj, sort_keys=True)
        sha256_hash = hashlib.sha256(deterministic_json.encode("utf-8")).hexdigest()
        fingerprint = f"sha256:{sha256_hash}"

        evidence = ReliabilityEvidence(
            timestamp=timestamp,
            component=component,
            event=event,
            status=status,
            evidence_level=evidence_level,
            sanitized_payload=sanitized_payload,
            fingerprint=fingerprint,
        )

        self._evidence_records.append(evidence)
        return evidence

    def get_all_evidence(self) -> List[ReliabilityEvidence]:
        return list(self._evidence_records)

    def clear(self) -> None:
        self._evidence_records.clear()
