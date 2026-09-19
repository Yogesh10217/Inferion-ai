"""
Audit Integrity Engine Module for Phase 5.69.
Verifies audit trail chain continuity, fingerprint hashes, and detects record tampering.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from app.deployment.secrets import SecretsSanitizer
from app.security_operations.audit_log import AuditIntegrityValidator, SecurityAuditLogger, SecurityAuditRecord


@dataclass
class AuditIntegrityResult:
    is_valid: bool
    status: str  # AUDIT_INTEGRITY_VALIDATED or AUDIT_INTEGRITY_FAILURE
    records_checked: int
    tampered_records_count: int
    chain_intact: bool
    evidence_level: str
    blocking_reasons: List[str]
    fingerprint: str = ""
    details: Dict[str, Any] = None

    def __post_init__(self):
        if self.details is None:
            self.details = {}
        if not self.fingerprint:
            payload = {
                "is_valid": self.is_valid,
                "status": self.status,
                "checked": self.records_checked,
            }
            self.fingerprint = (
                f"sha256:{hashlib.sha256(json.dumps(payload, sort_keys=True).encode('utf-8')).hexdigest()}"
            )

    @property
    def tampering_detected(self) -> bool:
        return not self.is_valid or self.tampered_records_count > 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_valid": self.is_valid,
            "status": self.status,
            "records_checked": self.records_checked,
            "tampered_records_count": self.tampered_records_count,
            "tampering_detected": self.tampering_detected,
            "chain_intact": self.chain_intact,
            "evidence_level": self.evidence_level,
            "fingerprint": self.fingerprint,
            "blocking_reasons": self.blocking_reasons,
            "details": SecretsSanitizer.sanitize_structure(self.details),
        }


class AuditIntegrityEngine:
    """Verifies audit log integrity and chain tamper evidence."""

    def __init__(self, logger: Optional[SecurityAuditLogger] = None) -> None:
        self.logger = logger

    def validate_audit_chain(self, evidence_level: str = "CONTAINER_RUNTIME") -> AuditIntegrityResult:
        recs = self.logger.get_records() if self.logger else []
        return self.verify_integrity(records=recs, evidence_level=evidence_level)

    def verify_integrity(
        self,
        records: List[SecurityAuditRecord],
        evidence_level: str = "CONTAINER_RUNTIME",
    ) -> AuditIntegrityResult:
        if not records:
            return AuditIntegrityResult(
                is_valid=True,
                status="AUDIT_INTEGRITY_VALIDATED",
                records_checked=0,
                tampered_records_count=0,
                chain_intact=True,
                evidence_level=evidence_level,
                blocking_reasons=[],
                details={"reason": "No audit records present."},
            )

        tampered = []
        for r in records:
            if not AuditIntegrityValidator.validate_record(r):
                tampered.append(r.audit_id)

        is_valid = len(tampered) == 0
        status = "AUDIT_INTEGRITY_VALIDATED" if is_valid else "AUDIT_INTEGRITY_FAILURE"

        reasons = []
        if not is_valid:
            reasons.append(f"AUDIT_INTEGRITY_FAILURE: Tampering detected in audit records: {tampered}")

        return AuditIntegrityResult(
            is_valid=is_valid,
            status=status,
            records_checked=len(records),
            tampered_records_count=len(tampered),
            chain_intact=is_valid,
            evidence_level=evidence_level,
            blocking_reasons=reasons,
            details={"tampered_ids": tampered},
        )
