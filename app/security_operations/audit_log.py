"""
Security Audit Log Module for Phase 5.69.
Generates immutable audit records with SHA-256 fingerprints (sha256:<64 hex>).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
import hashlib
import json
from typing import Any, Dict, List, Optional
import uuid

from app.deployment.secrets import SecretsSanitizer


@dataclass
class SecurityAuditRecord:
    audit_id: str
    timestamp: str
    actor_type: str
    action: str
    resource: str
    result: str
    evidence_level: str
    event_type: str = ""
    severity: str = "INFO"
    description: str = ""
    actor: str = ""
    resource_id: str = ""
    previous_hash: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    fingerprint: Optional[str] = None

    @property
    def record_hash(self) -> str:
        return self.fingerprint or ""

    def compute_fingerprint(self) -> str:
        sanitized_details = SecretsSanitizer.sanitize_structure(self.details)
        raw_payload = {
            "audit_id": self.audit_id,
            "timestamp": self.timestamp,
            "actor_type": self.actor_type,
            "action": self.action,
            "resource": self.resource,
            "result": self.result,
            "event_type": self.event_type,
            "severity": self.severity,
            "description": self.description,
            "actor": self.actor,
            "resource_id": self.resource_id,
            "previous_hash": self.previous_hash,
            "evidence_level": self.evidence_level,
            "details": sanitized_details,
        }
        deterministic_json = json.dumps(raw_payload, sort_keys=True)
        hash_hex = hashlib.sha256(deterministic_json.encode("utf-8")).hexdigest()
        return f"sha256:{hash_hex}"

    def __post_init__(self) -> None:
        if not self.fingerprint:
            self.fingerprint = self.compute_fingerprint()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "audit_id": self.audit_id,
            "timestamp": self.timestamp,
            "actor_type": self.actor_type,
            "action": SecretsSanitizer.sanitize_string(self.action),
            "resource": self.resource,
            "result": self.result,
            "event_type": self.event_type,
            "severity": self.severity,
            "description": SecretsSanitizer.sanitize_string(self.description),
            "actor": self.actor,
            "resource_id": self.resource_id,
            "previous_hash": self.previous_hash,
            "record_hash": self.record_hash,
            "evidence_level": self.evidence_level,
            "details": SecretsSanitizer.sanitize_structure(self.details),
            "fingerprint": self.fingerprint,
        }


class SecurityAuditLogger:
    """Logs immutable, secret-sanitized security audit events."""

    def __init__(self) -> None:
        self.records: List[SecurityAuditRecord] = []

    @property
    def _records(self) -> List[SecurityAuditRecord]:
        return self.records

    def get_records(self) -> List[SecurityAuditRecord]:
        return self.records

    def log_event(
        self,
        event_type: str = "SECURITY_EVENT",
        severity: str = "INFO",
        description: str = "",
        actor: str = "SYSTEM",
        resource_id: str = "platform",
        actor_type: Optional[str] = None,
        action: Optional[str] = None,
        resource: Optional[str] = None,
        result: str = "SUCCESS",
        evidence_level: str = "CONTAINER_RUNTIME",
        metadata: Optional[Dict[str, Any]] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> SecurityAuditRecord:
        now_iso = datetime.now(timezone.utc).isoformat()
        audit_id = f"audit-{uuid.uuid4().hex[:8]}"

        act_type = actor_type or actor or "SYSTEM"
        act_str = action or event_type or "SECURITY_ACTION"
        res_str = resource or resource_id or "platform"
        desc_str = description or act_str

        prev_hash = self.records[-1].record_hash if self.records else ""

        record = SecurityAuditRecord(
            audit_id=audit_id,
            timestamp=now_iso,
            actor_type=act_type,
            action=SecretsSanitizer.sanitize_string(act_str),
            resource=res_str,
            result=result,
            event_type=event_type,
            severity=severity,
            description=SecretsSanitizer.sanitize_string(desc_str),
            actor=actor,
            resource_id=resource_id,
            previous_hash=prev_hash,
            evidence_level=evidence_level,
            details=SecretsSanitizer.sanitize_structure(details or metadata or {}),
        )
        self.records.append(record)
        return record


class AuditIntegrityValidator:
    """Validates individual audit record fingerprints."""

    @classmethod
    def validate_record(cls, record: SecurityAuditRecord) -> bool:
        expected_fp = record.compute_fingerprint()
        return record.fingerprint == expected_fp
