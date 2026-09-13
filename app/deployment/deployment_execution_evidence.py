from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.deployment.secrets import SecretsSanitizer


@dataclass
class DeploymentExecutionEvidenceRecord:
    evidence_id: str
    category: str
    execution_status: str
    timestamp: str
    raw_payload: Dict[str, Any]
    sanitized_payload: Dict[str, Any]
    fingerprint: str

    def sanitized_dict(self) -> Dict[str, Any]:
        return SecretsSanitizer.sanitize_structure({
            "evidence_id": self.evidence_id,
            "category": self.category,
            "execution_status": self.execution_status,
            "timestamp": self.timestamp,
            "sanitized_payload": self.sanitized_payload,
            "fingerprint": self.fingerprint,
        })


class DeploymentExecutionEvidenceCollector:
    """Collects, sanitizes, formats, and SHA-256 fingerprints Phase 5.67 deployment execution evidence records."""

    @classmethod
    def collect_evidence(
        cls, evidence_id: str, category: str, execution_status: str, payload: Dict[str, Any]
    ) -> DeploymentExecutionEvidenceRecord:
        now = datetime.now(timezone.utc).isoformat()
        sanitized = SecretsSanitizer.sanitize_structure(payload)

        # Deterministic SHA-256 fingerprint of sanitized payload
        canonical_json = json.dumps({
            "evidence_id": evidence_id,
            "category": category,
            "status": execution_status,
            "payload": sanitized,
        }, sort_keys=True)
        fp = f"sha256:{hashlib.sha256(canonical_json.encode('utf-8')).hexdigest()}"

        return DeploymentExecutionEvidenceRecord(
            evidence_id=evidence_id,
            category=category,
            execution_status=execution_status,
            timestamp=now,
            raw_payload=payload,
            sanitized_payload=sanitized,
            fingerprint=fp,
        )
