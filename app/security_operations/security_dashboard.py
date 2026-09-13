"""
Phase 5.69 — Security Dashboard Snapshot Module.

Aggregates operational security posture, vulnerability counts, continuous risk,
compliance status, audit integrity, active exceptions, and certification status
into a unified real-time dashboard snapshot for operational security visibility.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import hashlib
import json

from app.deployment.secrets import get_secrets_sanitizer
from app.security_operations.security_posture import SecurityPostureResult
from app.security_operations.security_metrics import SecurityMetricsResult
from app.security_operations.security_risk_engine import RiskAssessment
from app.security_operations.compliance_governance import ComplianceResult
from app.security_operations.audit_integrity import AuditIntegrityResult
from app.security_operations.security_certification import SecurityCertificationResult


@dataclass
class SecurityDashboardSnapshot:
    """Unified security operations dashboard snapshot."""
    timestamp: str
    overall_posture_score: float
    overall_posture_status: str
    certification_decision: str
    risk_level: str
    total_vulnerabilities: int
    critical_vulnerabilities: int
    high_vulnerabilities: int
    open_vulnerabilities: int
    active_exceptions_count: int
    compliance_score: float
    audit_tamper_detected: bool
    metrics_summary: Dict[str, Any]
    active_threats_count: int
    is_production: bool
    fingerprint: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return get_secrets_sanitizer().sanitize_dict({
            "timestamp": self.timestamp,
            "overall_posture_score": self.overall_posture_score,
            "overall_posture_status": self.overall_posture_status,
            "certification_decision": self.certification_decision,
            "risk_level": self.risk_level,
            "total_vulnerabilities": self.total_vulnerabilities,
            "critical_vulnerabilities": self.critical_vulnerabilities,
            "high_vulnerabilities": self.high_vulnerabilities,
            "open_vulnerabilities": self.open_vulnerabilities,
            "active_exceptions_count": self.active_exceptions_count,
            "compliance_score": self.compliance_score,
            "audit_tamper_detected": self.audit_tamper_detected,
            "metrics_summary": self.metrics_summary,
            "active_threats_count": self.active_threats_count,
            "is_production": self.is_production,
            "fingerprint": self.fingerprint,
            "metadata": self.metadata,
        })


class SecurityDashboard:
    """Generates real-time security dashboard snapshots."""

    def __init__(self):
        self._sanitizer = get_secrets_sanitizer()

    def generate_snapshot(
        self,
        posture_result: SecurityPostureResult,
        metrics_result: SecurityMetricsResult,
        risk_assessment: RiskAssessment,
        compliance_result: ComplianceResult,
        audit_integrity: AuditIntegrityResult,
        certification_result: SecurityCertificationResult,
        active_exceptions_count: int = 0,
        active_threats_count: int = 0,
        is_production: bool = False,
    ) -> SecurityDashboardSnapshot:
        now_str = datetime.now(timezone.utc).isoformat()
        
        payload_for_fp = {
            "posture": posture_result.score,
            "cert": certification_result.decision,
            "risk": risk_assessment.overall_risk_level,
            "compliance": compliance_result.overall_compliance_score,
            "is_prod": is_production,
        }
        fp_hash = hashlib.sha256(json.dumps(payload_for_fp, sort_keys=True).encode("utf-8")).hexdigest()
        fingerprint = f"sha256:{fp_hash}"

        snapshot = SecurityDashboardSnapshot(
            timestamp=now_str,
            overall_posture_score=posture_result.score,
            overall_posture_status=posture_result.status,
            certification_decision=certification_result.decision,
            risk_level=risk_assessment.overall_risk_level,
            total_vulnerabilities=posture_result.vulnerability_assessment.total_vulnerabilities,
            critical_vulnerabilities=posture_result.vulnerability_assessment.critical_count,
            high_vulnerabilities=posture_result.vulnerability_assessment.high_count,
            open_vulnerabilities=posture_result.vulnerability_assessment.open_count,
            active_exceptions_count=active_exceptions_count,
            compliance_score=compliance_result.overall_compliance_score,
            audit_tamper_detected=audit_integrity.tampering_detected,
            metrics_summary=metrics_result.to_dict(),
            active_threats_count=active_threats_count,
            is_production=is_production,
            fingerprint=fingerprint,
            metadata={
                "gating_passed": certification_result.is_certified,
                "sanitized": True,
            }
        )

        return snapshot
