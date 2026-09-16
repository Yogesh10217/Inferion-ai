"""
Security Exception Management Module for Phase 5.69.
Manages time-bound security policy exceptions and automatically enforces TTL expiration.
"""

from __future__ import annotations

import hashlib
import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from app.deployment.secrets import SecretsSanitizer


class SecurityExceptionStatus(str, Enum):
    REQUESTED = "REQUESTED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"
    REVOKED = "REVOKED"


@dataclass
class SecurityException:
    exception_id: str
    rule_id: str = "SEC-RULE-001"
    reason: str = ""
    risk_level: str = "MEDIUM"
    approver: str = "security_team"
    expires_at: str = ""  # ISO timestamp
    vulnerability_id: str = ""
    policy_id: str = ""
    requested_by: str = ""
    granted_at: str = ""
    status: SecurityExceptionStatus = SecurityExceptionStatus.APPROVED
    fingerprint: str = ""
    evidence: Dict[str, Any] = field(default_factory=dict)
    is_active_flag: Optional[bool] = None

    def __post_init__(self):
        if not self.granted_at:
            self.granted_at = datetime.now(timezone.utc).isoformat()
        if not self.expires_at:
            self.expires_at = (datetime.now(timezone.utc) + timedelta(days=7)).isoformat()
        if not self.fingerprint:
            payload = {
                "id": self.exception_id,
                "reason": self.reason,
                "expires_at": self.expires_at,
            }
            self.fingerprint = f"sha256:{hashlib.sha256(json.dumps(payload, sort_keys=True).encode('utf-8')).hexdigest()}"
        self.check_expiration()

    def check_expiration(self) -> SecurityExceptionStatus:
        if self.status == SecurityExceptionStatus.APPROVED:
            now = datetime.now(timezone.utc)
            try:
                exp_clean = self.expires_at.replace("Z", "+00:00")
                exp = datetime.fromisoformat(exp_clean)
                if now > exp:
                    self.status = SecurityExceptionStatus.EXPIRED
            except ValueError:
                pass
        return self.status

    @property
    def is_active(self) -> bool:
        stat = self.check_expiration()
        return stat == SecurityExceptionStatus.APPROVED

    def to_dict(self) -> Dict[str, Any]:
        self.check_expiration()
        return {
            "exception_id": self.exception_id,
            "rule_id": self.rule_id,
            "vulnerability_id": self.vulnerability_id,
            "policy_id": self.policy_id,
            "reason": SecretsSanitizer.sanitize_string(self.reason),
            "risk_level": self.risk_level,
            "approver": self.approver,
            "requested_by": self.requested_by,
            "granted_at": self.granted_at,
            "expires_at": self.expires_at,
            "is_active": self.is_active,
            "status": self.status.value if isinstance(self.status, Enum) else str(self.status),
            "fingerprint": self.fingerprint,
            "evidence": SecretsSanitizer.sanitize_structure(self.evidence or {}),
        }


class SecurityExceptionManager:
    """Manages active security policy exceptions and enforces expiration."""

    def __init__(self) -> None:
        self.exceptions: Dict[str, SecurityException] = {}

    @property
    def _exceptions(self) -> Dict[str, SecurityException]:
        return self.exceptions

    def grant_exception(
        self,
        vulnerability_id: str = "",
        policy_id: str = "",
        reason: str = "",
        requested_by: str = "",
        duration_days: int = 7,
        rule_id: str = "",
        approver: str = "",
        risk_level: str = "MEDIUM",
        evidence: Optional[Dict[str, Any]] = None,
    ) -> SecurityException:
        now = datetime.now(timezone.utc)
        exp_iso = (now + timedelta(days=duration_days)).isoformat()
        exc_id = f"EX-{uuid.uuid4().hex[:8]}"

        exc = SecurityException(
            exception_id=exc_id,
            rule_id=rule_id or policy_id or "SEC-RULE-001",
            vulnerability_id=vulnerability_id,
            policy_id=policy_id,
            reason=SecretsSanitizer.sanitize_string(reason),
            risk_level=risk_level,
            approver=approver or requested_by or "security_team",
            requested_by=requested_by,
            granted_at=now.isoformat(),
            expires_at=exp_iso,
            status=SecurityExceptionStatus.APPROVED,
            evidence=SecretsSanitizer.sanitize_structure(evidence or {}),
        )
        self.exceptions[exc_id] = exc
        return exc

    def request_exception(
        self,
        exception_id: str,
        rule_id: str,
        reason: str,
        approver: str,
        expires_at: str,
        risk_level: str = "MEDIUM",
        evidence: Optional[Dict[str, Any]] = None,
    ) -> SecurityException:
        exc = SecurityException(
            exception_id=exception_id,
            rule_id=rule_id,
            reason=SecretsSanitizer.sanitize_string(reason),
            risk_level=risk_level,
            approver=approver,
            expires_at=expires_at,
            status=SecurityExceptionStatus.APPROVED,
            evidence=SecretsSanitizer.sanitize_structure(evidence or {}),
        )
        self.exceptions[exception_id] = exc
        return exc

    def get_active_exceptions(self) -> List[SecurityException]:
        return [e for e in self.exceptions.values() if e.is_active]

    def get_exception(self, exception_id: str) -> Optional[SecurityException]:
        exc = self.exceptions.get(exception_id)
        if exc:
            exc.check_expiration()
        return exc

    def is_exception_valid(self, exception_id: str) -> bool:
        exc = self.get_exception(exception_id)
        if not exc:
            return False
        return exc.is_active
