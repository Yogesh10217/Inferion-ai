"""
Security Evidence Module for Phase 5.69.
Collects, sanitizes, and seals security evidence payloads with SHA-256 fingerprints.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
from enum import Enum
from typing import Any, Dict
import uuid

from app.deployment.secrets import SecretsSanitizer


class SecurityEvidenceLevel(str, Enum):
    STATIC = "STATIC"
    UNIT_TEST = "UNIT_TEST"
    INTEGRATION_TEST = "INTEGRATION_TEST"
    ASGI_RUNTIME = "ASGI_RUNTIME"
    SIMULATION_RUNTIME = "SIMULATION_RUNTIME"
    CONTAINER_RUNTIME = "CONTAINER_RUNTIME"
    INFRASTRUCTURE_RUNTIME = "INFRASTRUCTURE_RUNTIME"
    PRODUCTION_RUNTIME = "PRODUCTION_RUNTIME"


@dataclass
class SecurityEvidence:
    evidence_id: str
    timestamp: str
    evidence_level: SecurityEvidenceLevel
    canonical_payload: Dict[str, Any]
    sha256_fingerprint: str

    @property
    def fingerprint(self) -> str:
        return self.sha256_fingerprint

    def to_dict(self) -> Dict[str, Any]:
        ev_lvl_str = self.evidence_level.value if isinstance(self.evidence_level, Enum) else str(self.evidence_level)
        return {
            "evidence_id": self.evidence_id,
            "timestamp": self.timestamp,
            "evidence_level": ev_lvl_str,
            "canonical_payload": self.canonical_payload,
            "sha256_fingerprint": self.sha256_fingerprint,
            "fingerprint": self.fingerprint,
        }


class SecurityEvidenceCollector:
    """Collects and produces SHA-256 fingerprinted security evidence records."""

    def collect_evidence(
        self,
        posture_result: Any,
        policy_result: Any,
        compliance_result: Any,
        risk_assessment: Any,
        certification_result: Any,
        is_production: bool = False,
    ) -> SecurityEvidence:
        raw_payload = {
            "posture": posture_result.to_dict() if hasattr(posture_result, "to_dict") else str(posture_result),
            "policy": policy_result.to_dict() if hasattr(policy_result, "to_dict") else str(policy_result),
            "compliance": compliance_result.to_dict() if hasattr(compliance_result, "to_dict") else str(compliance_result),
            "risk": risk_assessment.to_dict() if hasattr(risk_assessment, "to_dict") else str(risk_assessment),
            "certification": certification_result.to_dict() if hasattr(certification_result, "to_dict") else str(certification_result),
            "is_production": is_production,
        }
        ev_level = SecurityEvidenceLevel.PRODUCTION_RUNTIME if is_production else SecurityEvidenceLevel.CONTAINER_RUNTIME
        ev_id = f"EVID-{uuid.uuid4().hex[:8]}"

        return self.create_evidence(
            raw_payload=raw_payload,
            evidence_level=ev_level,
            evidence_id=ev_id,
        )

    def create_evidence(
        self,
        raw_payload: Dict[str, Any],
        evidence_level: SecurityEvidenceLevel = SecurityEvidenceLevel.CONTAINER_RUNTIME,
        evidence_id: str = "EVID-001",
    ) -> SecurityEvidence:
        now_iso = datetime.now(timezone.utc).isoformat()
        sanitized_payload = SecretsSanitizer.sanitize_structure(raw_payload)

        ev_lvl_str = evidence_level.value if isinstance(evidence_level, Enum) else str(evidence_level)
        canonical = {
            "evidence_id": evidence_id,
            "evidence_level": ev_lvl_str,
            "data": sanitized_payload,
        }

        deterministic_json = json.dumps(canonical, sort_keys=True)
        fingerprint = f"sha256:{hashlib.sha256(deterministic_json.encode('utf-8')).hexdigest()}"

        return SecurityEvidence(
            evidence_id=evidence_id,
            timestamp=now_iso,
            evidence_level=evidence_level,
            canonical_payload=canonical,
            sha256_fingerprint=fingerprint,
        )
