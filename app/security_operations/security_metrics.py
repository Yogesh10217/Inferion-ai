"""
Security Metrics Module for Phase 5.69.
Calculates 8 deterministic security metrics without division by zero.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Dict, Optional

from app.deployment.secrets import SecretsSanitizer


@dataclass
class SecurityMetricsResult:
    security_policy_compliance_rate: float
    open_vulnerability_count: int
    critical_vulnerability_count: int
    security_event_rate: float
    auth_failure_rate: float
    secret_exposure_count: int
    audit_integrity_rate: float
    security_certification_rate: float
    fingerprint: str = ""
    details: Dict[str, Any] = None

    def __post_init__(self):
        if self.details is None:
            self.details = {}
        if not self.fingerprint:
            payload = {
                "comp_rate": self.security_policy_compliance_rate,
                "open_vulns": self.open_vulnerability_count,
            }
            self.fingerprint = f"sha256:{hashlib.sha256(json.dumps(payload, sort_keys=True).encode('utf-8')).hexdigest()}"

    @property
    def posture_index(self) -> float:
        return self.security_policy_compliance_rate

    @property
    def vulnerability_density(self) -> float:
        return float(self.open_vulnerability_count)

    @property
    def patch_compliance_rate(self) -> float:
        return 100.0 if self.open_vulnerability_count == 0 else 80.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "security_policy_compliance_rate": round(max(0.0, min(100.0, self.security_policy_compliance_rate)), 2),
            "posture_index": round(max(0.0, min(100.0, self.posture_index)), 2),
            "vulnerability_density": self.vulnerability_density,
            "patch_compliance_rate": self.patch_compliance_rate,
            "open_vulnerability_count": max(0, self.open_vulnerability_count),
            "critical_vulnerability_count": max(0, self.critical_vulnerability_count),
            "security_event_rate": round(max(0.0, self.security_event_rate), 2),
            "auth_failure_rate": round(max(0.0, min(100.0, self.auth_failure_rate)), 2),
            "secret_exposure_count": max(0, self.secret_exposure_count),
            "audit_integrity_rate": round(max(0.0, min(100.0, self.audit_integrity_rate)), 2),
            "security_certification_rate": round(max(0.0, min(100.0, self.security_certification_rate)), 2),
            "fingerprint": self.fingerprint,
            "details": SecretsSanitizer.sanitize_structure(self.details),
        }


class SecurityMetricsCalculator:
    """Calculates security KPIs deterministically."""

    def calculate_metrics(
        self,
        posture_score: float = 100.0,
        vulnerability_assessment: Optional[Any] = None,
        active_exceptions_count: int = 0,
        compliance_score: float = 100.0,
        is_production: bool = False,
        total_policies_checked: int = 10,
        compliant_policies_count: int = 10,
        open_vulns: int = 0,
        crit_vulns: int = 0,
        security_events_count: int = 0,
        total_auth_requests: int = 100,
        failed_auth_requests: int = 0,
        secret_exposures: int = 0,
        total_audit_records: int = 10,
        tampered_audit_records: int = 0,
        is_certified: bool = True,
    ) -> SecurityMetricsResult:
        if vulnerability_assessment:
            open_vulns = getattr(vulnerability_assessment, "open_count", open_vulns)
            crit_vulns = getattr(vulnerability_assessment, "critical_count", crit_vulns)

        policy_rate = compliance_score if compliance_score is not None else posture_score
        auth_fail_rate = (failed_auth_requests / total_auth_requests * 100.0) if total_auth_requests > 0 else 0.0
        valid_audits = max(0, total_audit_records - tampered_audit_records)
        audit_rate = (valid_audits / total_audit_records * 100.0) if total_audit_records > 0 else 100.0
        cert_rate = 100.0 if is_certified else 0.0

        return SecurityMetricsResult(
            security_policy_compliance_rate=policy_rate,
            open_vulnerability_count=open_vulns,
            critical_vulnerability_count=crit_vulns,
            security_event_rate=float(security_events_count),
            auth_failure_rate=auth_fail_rate,
            secret_exposure_count=secret_exposures,
            audit_integrity_rate=audit_rate,
            security_certification_rate=cert_rate,
            details={"is_certified": is_certified, "active_exceptions": active_exceptions_count},
        )
