"""
Phase 5.70 - Recovery Audit Module.

Validates recovery history, state transition sequence, evidence integrity, timestamp ordering, and tampering detection.
Audit failures block reliability certification.
"""

from dataclasses import dataclass, field
from enum import Enum
import hashlib
import json
import time
from typing import Any, Dict, List, Optional

from app.reliability.reliability_evidence import ReliabilityEvidence, ReliabilityEvidenceLevel


@dataclass
class RecoveryAuditRecord:
    record_id: str
    timestamp: float
    event: str
    evidence_fingerprint: str
    sanitized_payload: Dict[str, Any]


@dataclass
class RecoveryAuditResult:
    valid: bool
    total_records: int
    tampering_detected: bool
    timestamp_ordering_valid: bool
    evidence_fingerprints_valid: bool
    errors: List[str]
    evidence_level: ReliabilityEvidenceLevel


class RecoveryAuditEngine:
    """Audits recovery evidence chains and transition histories for tampering and sequence integrity."""

    def __init__(self, evidence_level: ReliabilityEvidenceLevel = ReliabilityEvidenceLevel.SIMULATION_RUNTIME) -> None:
        self.evidence_level = evidence_level

    def audit_evidence_records(
        self,
        records: List[ReliabilityEvidence],
        executed: bool = True,
    ) -> RecoveryAuditResult:
        if not executed:
            return RecoveryAuditResult(
                valid=False,
                total_records=0,
                tampering_detected=False,
                timestamp_ordering_valid=False,
                evidence_fingerprints_valid=False,
                errors=["Recovery audit not executed."],
                evidence_level=self.evidence_level,
            )

        errors: List[str] = []
        tampering_detected = False
        timestamp_ordering_valid = True
        evidence_fingerprints_valid = True

        last_timestamp = 0.0

        for idx, rec in enumerate(records):
            # Check timestamp ordering
            if rec.timestamp < last_timestamp:
                timestamp_ordering_valid = False
                errors.append(f"Record {idx} timestamp {rec.timestamp} is earlier than previous {last_timestamp}.")
            last_timestamp = rec.timestamp

            # Validate fingerprint
            canonical_obj = {
                "component": rec.component,
                "event": rec.event,
                "evidence_level": rec.evidence_level.value if isinstance(rec.evidence_level, ReliabilityEvidenceLevel) else str(rec.evidence_level),
                "sanitized_payload": rec.sanitized_payload,
                "status": rec.status,
                "timestamp": rec.timestamp,
            }
            deterministic_json = json.dumps(canonical_obj, sort_keys=True)
            sha256_hash = hashlib.sha256(deterministic_json.encode("utf-8")).hexdigest()
            expected_fp = f"sha256:{sha256_hash}"

            if rec.fingerprint != expected_fp:
                evidence_fingerprints_valid = False
                tampering_detected = True
                errors.append(f"Record {idx} fingerprint mismatch! Found {rec.fingerprint}, computed {expected_fp}.")

        is_valid = timestamp_ordering_valid and evidence_fingerprints_valid and not tampering_detected

        return RecoveryAuditResult(
            valid=is_valid,
            total_records=len(records),
            tampering_detected=tampering_detected,
            timestamp_ordering_valid=timestamp_ordering_valid,
            evidence_fingerprints_valid=evidence_fingerprints_valid,
            errors=errors,
            evidence_level=self.evidence_level,
        )
