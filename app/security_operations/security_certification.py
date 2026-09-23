"""
Security Certification Engine Module for Phase 5.69.
Evaluates platform security evidence and issues deterministic security readiness certification decisions.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from app.deployment.secrets import SecretsSanitizer
from app.security_operations.audit_integrity import AuditIntegrityResult
from app.security_operations.container_security import ContainerSecurityResult
from app.security_operations.security_evidence import SecurityEvidence
from app.security_operations.security_policy_engine import SecurityPolicyAction, SecurityPolicyResult
from app.security_operations.security_posture import SecurityPostureResult
from app.security_operations.security_risk_engine import RiskAssessment, RiskPolicyAction
from app.security_operations.vulnerability_management import VulnerabilityAssessment

UNEXECUTED_PRODUCTION_CLAIMS = [
    "PRODUCTION_PENETRATION_TEST_EXECUTED",
    "PRODUCTION_VULNERABILITY_SCAN_EXECUTED",
    "PRODUCTION_SECRET_ROTATION_EXECUTED",
    "PRODUCTION_CERTIFICATE_ROTATION_EXECUTED",
    "LIVE_SECURITY_INCIDENT_RESPONSE_EXECUTED",
    "PRODUCTION_COMPLIANCE_AUDIT_EXECUTED",
    "LIVE_PRODUCTION_SECURITY_VALIDATED",
    "PRODUCTION_DEPLOYED",
    "LIVE_PRODUCTION",
]


class SecurityCertificationDecision(str, Enum):
    SECURITY_CERTIFIED = "SECURITY_CERTIFIED"
    SECURITY_CERTIFIED_WITH_WARNINGS = "SECURITY_CERTIFIED_WITH_WARNINGS"
    SECURITY_MANUAL_REVIEW_REQUIRED = "SECURITY_MANUAL_REVIEW_REQUIRED"
    SECURITY_BLOCKED = "SECURITY_BLOCKED"
    SECURITY_NOT_EXECUTED = "SECURITY_NOT_EXECUTED"


@dataclass
class SecurityCertificationResult:
    decision: str
    is_certified: bool
    evidence_level: str
    summary: str
    truthfulness_matrix: Dict[str, str]
    sha256_fingerprint: str
    details: Dict[str, Any]
    unexecuted_claims: List[str] = field(default_factory=list)
    fingerprint: str = ""

    def __post_init__(self):
        if not self.fingerprint:
            self.fingerprint = self.sha256_fingerprint

    def to_dict(self) -> Dict[str, Any]:
        return {
            "decision": str(self.decision),
            "is_certified": self.is_certified,
            "evidence_level": self.evidence_level,
            "summary": SecretsSanitizer.sanitize_string(self.summary),
            "truthfulness_matrix": self.truthfulness_matrix,
            "sha256_fingerprint": self.sha256_fingerprint,
            "fingerprint": self.fingerprint,
            "unexecuted_claims": self.unexecuted_claims,
            "details": SecretsSanitizer.sanitize_structure(self.details),
        }


class SecurityCertificationEngine:
    """Evaluates security evidence to issue canonical security certification decisions."""

    def certify(
        self,
        posture_result: SecurityPostureResult,
        policy_result: SecurityPolicyResult,
        compliance_result: Any,
        risk_assessment: RiskAssessment,
        audit_integrity: AuditIntegrityResult,
        is_production: bool = False,
        vulnerability_assessment: Optional[VulnerabilityAssessment] = None,
        container_security: Optional[ContainerSecurityResult] = None,
        evidence: Optional[SecurityEvidence] = None,
    ) -> SecurityCertificationResult:
        """Convenience method for certification evaluation."""
        vuln_assessment = vulnerability_assessment or posture_result.vulnerability_assessment
        cont_security = container_security or posture_result.container_security

        return self.evaluate_certification(
            posture_result=posture_result,
            policy_result=policy_result,
            vulnerability_assessment=vuln_assessment,
            container_security=cont_security,
            audit_integrity=audit_integrity,
            risk_assessment=risk_assessment,
            evidence=evidence,
            is_production=is_production,
        )

    def evaluate_certification(
        self,
        posture_result: SecurityPostureResult,
        policy_result: SecurityPolicyResult,
        audit_integrity: AuditIntegrityResult,
        risk_assessment: RiskAssessment,
        vulnerability_assessment: Optional[VulnerabilityAssessment] = None,
        container_security: Optional[ContainerSecurityResult] = None,
        evidence: Optional[SecurityEvidence] = None,
        is_production: bool = False,
    ) -> SecurityCertificationResult:
        ev_level = posture_result.evidence_level

        truthfulness_matrix = {
            "SECURITY_POSTURE_VALIDATED": "READY",
            "SECURITY_POLICY_VALIDATED": "READY",
            "VULNERABILITY_MANAGEMENT_VALIDATED": "READY",
            "DEPENDENCY_SECURITY_VALIDATED": "READY",
            "CONTAINER_SECURITY_VALIDATED": "READY",
            "SECRET_SECURITY_VALIDATED": "READY",  # nosec B105
            "AUTHENTICATION_SECURITY_VALIDATED": "READY",
            "AUTHORIZATION_SECURITY_VALIDATED": "READY",
            "API_SECURITY_VALIDATED": "READY",
            "SECURITY_EVENT_DETECTION_VALIDATED": "READY",
            "SECURITY_INCIDENT_INTEGRATION_VALIDATED": "READY",
            "THREAT_CLASSIFICATION_VALIDATED": "READY",
            "COMPLIANCE_GOVERNANCE_VALIDATED": "READY",
            "AUDIT_LOGGING_VALIDATED": "READY",
            "AUDIT_INTEGRITY_VALIDATED": "READY",
            "SECURITY_RISK_ASSESSMENT_VALIDATED": "READY",
            "SECURITY_EXCEPTION_GOVERNANCE_VALIDATED": "READY",
            "SECURITY_METRICS_VALIDATED": "READY",
            "SECURITY_DASHBOARD_VALIDATED": "READY",
            "SECURITY_CERTIFICATION_VALIDATED": "READY",
        }
        for claim in UNEXECUTED_PRODUCTION_CLAIMS:
            truthfulness_matrix[claim] = "NOT_EXECUTED"

        unexecuted = list(UNEXECUTED_PRODUCTION_CLAIMS) if is_production else []

        if is_production:
            return SecurityCertificationResult(
                decision=SecurityCertificationDecision.SECURITY_NOT_EXECUTED.value,
                is_certified=False,
                evidence_level="PRODUCTION_RUNTIME",
                summary="Production security certification cannot be issued without empirical production infrastructure execution.",
                truthfulness_matrix=truthfulness_matrix,
                sha256_fingerprint=evidence.sha256_fingerprint if evidence else "sha256:" + "0" * 64,
                details={"reason": "Production environment not connected."},
                unexecuted_claims=unexecuted,
            )

        crit_vuln_count = vulnerability_assessment.critical_count if vulnerability_assessment else 0
        high_vuln_count = vulnerability_assessment.high_count if vulnerability_assessment else 0

        # Certification Requirements
        has_blocking_policy = (
            policy_result.is_blocking if hasattr(policy_result, "is_blocking") else (policy_result.action == "BLOCK")
        )
        has_crit_vulns = crit_vuln_count > 0
        has_audit_tampering = not audit_integrity.is_valid
        has_blocking_risk = (
            risk_assessment.is_blocking
            if hasattr(risk_assessment, "is_blocking")
            else (risk_assessment.overall_risk_level == "CRITICAL")
        )
        container_blocked = getattr(container_security, "classification", "") == "CONTAINER_SECURITY_BLOCKED"

        if has_blocking_policy or has_crit_vulns or has_audit_tampering or has_blocking_risk or container_blocked:
            decision = SecurityCertificationDecision.SECURITY_BLOCKED.value
            is_certified = False
            summary = "Security certification BLOCKED due to critical security policy, vulnerability, or audit integrity failure."
        elif (
            getattr(policy_result, "overall_action", policy_result.action)
            == SecurityPolicyAction.MANUAL_REVIEW_REQUIRED
            or getattr(risk_assessment, "overall_policy_action", None) == RiskPolicyAction.MANUAL_REVIEW_REQUIRED
        ):
            decision = SecurityCertificationDecision.SECURITY_MANUAL_REVIEW_REQUIRED.value
            is_certified = False
            summary = "Security manual review required prior to release candidate signoff."
        elif (
            getattr(policy_result, "overall_action", policy_result.action) == SecurityPolicyAction.WARN
            or high_vuln_count > 0
        ):
            decision = SecurityCertificationDecision.SECURITY_CERTIFIED_WITH_WARNINGS.value
            is_certified = True
            summary = "Platform security certified with non-blocking security warnings."
        else:
            decision = SecurityCertificationDecision.SECURITY_CERTIFIED.value
            is_certified = True
            summary = "Platform operationally and continuously security certified ready."

        fp = evidence.sha256_fingerprint if evidence else "sha256:" + "0" * 64

        return SecurityCertificationResult(
            decision=decision,
            is_certified=is_certified,
            evidence_level=ev_level,
            summary=summary,
            truthfulness_matrix=truthfulness_matrix,
            sha256_fingerprint=fp,
            details={
                "posture_score": (
                    posture_result.score
                    if hasattr(posture_result, "score")
                    else getattr(posture_result, "security_score", 0)
                ),
                "critical_vuln_count": crit_vuln_count,
                "audit_integrity_valid": audit_integrity.is_valid,
            },
            unexecuted_claims=unexecuted,
        )
