"""
Phase 5.69 — Security Operations Orchestrator Module.

Canonical orchestrator that coordinates all Security Operations & Compliance
Governance components into a unified execution flow:
- Posture evaluation (0-100 score)
- Policy enforcement (ALLOW, WARN, BLOCK, MANUAL_REVIEW_REQUIRED)
- Vulnerability management & dependency / container / secret / auth / API checks
- Incident & Alert integration (Phase 5.68 IncidentManager & AlertEngine)
- Threat classification (advisory decisions with auto_execution_blocked=True)
- Compliance governance & audit logging with SHA-256 tamper integrity
- Risk engine & TTL exception management
- Evidence collection & metric computation
- Security Certification (GO / NO-GO) & Dashboard snapshot generation
- Truthfulness boundary protection for unexecuted live production claims
"""

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.core.container import ServiceContainer
from app.deployment.secrets import get_secrets_sanitizer
from app.security_operations.api_security import APISecurityEvaluator
from app.security_operations.audit_integrity import AuditIntegrityEngine
from app.security_operations.audit_log import SecurityAuditLogger
from app.security_operations.authentication_security import AuthenticationSecurityEvaluator
from app.security_operations.authorization_security import AuthorizationSecurityEvaluator
from app.security_operations.compliance_governance import ComplianceGovernanceEngine, ComplianceResult
from app.security_operations.container_security import ContainerSecurityEvaluator
from app.security_operations.dependency_security import DependencySecurityEvaluator
from app.security_operations.secret_security import SecretSecurityEvaluator
from app.security_operations.security_certification import SecurityCertificationEngine, SecurityCertificationResult
from app.security_operations.security_dashboard import SecurityDashboard, SecurityDashboardSnapshot
from app.security_operations.security_event_detection import SecurityEventDetector
from app.security_operations.security_evidence import SecurityEvidence, SecurityEvidenceCollector
from app.security_operations.security_exception_management import SecurityExceptionManager
from app.security_operations.security_metrics import SecurityMetricsCalculator, SecurityMetricsResult
from app.security_operations.security_policy_engine import SecurityPolicyEngine, SecurityPolicyResult
from app.security_operations.security_posture import SecurityPostureEvaluator, SecurityPostureResult
from app.security_operations.security_risk_engine import RiskAssessment, SecurityRiskEngine
from app.security_operations.security_threat_classifier import SecurityThreatClassifier
from app.security_operations.vulnerability_management import VulnerabilityManager

# Import Phase 5.68 Incident & Alert engines if available
try:
    from app.operations.alert_engine import AlertEngine
    from app.operations.incident_management import IncidentManager

    SRE_AVAILABLE = True
except ImportError:
    SRE_AVAILABLE = False
    IncidentManager = None
    AlertEngine = None


@dataclass
class SecurityOperationsResult:
    """Consolidated result of a full Security Operations evaluation."""

    timestamp: str
    is_certified: bool
    certification_decision: str
    posture_score: float
    posture_status: str
    policy_action: str
    risk_level: str
    compliance_score: float
    audit_integrity_passed: bool
    is_production: bool
    unexecuted_claims: List[str]
    posture_result: SecurityPostureResult
    policy_result: SecurityPolicyResult
    compliance_result: ComplianceResult
    risk_assessment: RiskAssessment
    certification_result: SecurityCertificationResult
    metrics_result: SecurityMetricsResult
    dashboard_snapshot: SecurityDashboardSnapshot
    evidence: SecurityEvidence
    fingerprint: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return get_secrets_sanitizer().sanitize_dict(
            {
                "timestamp": self.timestamp,
                "is_certified": self.is_certified,
                "certification_decision": self.certification_decision,
                "posture_score": self.posture_score,
                "posture_status": self.posture_status,
                "policy_action": self.policy_action,
                "risk_level": self.risk_level,
                "compliance_score": self.compliance_score,
                "audit_integrity_passed": self.audit_integrity_passed,
                "is_production": self.is_production,
                "unexecuted_claims": self.unexecuted_claims,
                "posture": self.posture_result.to_dict(),
                "policy": self.policy_result.to_dict(),
                "compliance": self.compliance_result.to_dict(),
                "risk": self.risk_assessment.to_dict(),
                "certification": self.certification_result.to_dict(),
                "metrics": self.metrics_result.to_dict(),
                "dashboard": self.dashboard_snapshot.to_dict(),
                "evidence": self.evidence.to_dict(),
                "fingerprint": self.fingerprint,
                "metadata": self.metadata,
            }
        )


class SecurityOperationsOrchestrator:
    """
    Canonical Orchestrator for Enterprise AI Platform Security Operations & Compliance.
    Integrates all Phase 5.69 security engines with canonical ServiceContainer singleton
    and Phase 5.68 IncidentManager & AlertEngine.
    """

    def __init__(
        self,
        service_container: Optional[ServiceContainer] = None,
        incident_manager: Optional[Any] = None,
        alert_engine: Optional[Any] = None,
    ):
        self.service_container = service_container or ServiceContainer()
        self.sanitizer = get_secrets_sanitizer()

        # Instantiate components
        self.vulnerability_manager = VulnerabilityManager()
        self.dependency_evaluator = DependencySecurityEvaluator()
        self.container_evaluator = ContainerSecurityEvaluator()
        self.secret_evaluator = SecretSecurityEvaluator()
        self.auth_evaluator = AuthenticationSecurityEvaluator()
        self.authz_evaluator = AuthorizationSecurityEvaluator()
        self.api_evaluator = APISecurityEvaluator()

        self.posture_evaluator = SecurityPostureEvaluator(
            vulnerability_manager=self.vulnerability_manager,
            dependency_evaluator=self.dependency_evaluator,
            container_evaluator=self.container_evaluator,
            secret_evaluator=self.secret_evaluator,
            auth_evaluator=self.auth_evaluator,
            authz_evaluator=self.authz_evaluator,
            api_evaluator=self.api_evaluator,
        )

        self.policy_engine = SecurityPolicyEngine()
        self.event_detector = SecurityEventDetector(
            incident_manager=incident_manager,
            alert_engine=alert_engine,
        )
        self.threat_classifier = SecurityThreatClassifier()
        self.compliance_engine = ComplianceGovernanceEngine()
        self.audit_logger = SecurityAuditLogger()
        self.audit_integrity_engine = AuditIntegrityEngine(self.audit_logger)
        self.risk_engine = SecurityRiskEngine()
        self.exception_manager = SecurityExceptionManager()
        self.evidence_collector = SecurityEvidenceCollector()
        self.certification_engine = SecurityCertificationEngine()
        self.metrics_calculator = SecurityMetricsCalculator()
        self.dashboard = SecurityDashboard()

    def run_security_assessment(
        self,
        target_name: str = "Enterprise-AI-Platform",
        is_production: bool = False,
        env_config: Optional[Dict[str, Any]] = None,
        package_manifest: Optional[Dict[str, str]] = None,
        container_config: Optional[Dict[str, Any]] = None,
        auth_config: Optional[Dict[str, Any]] = None,
        authz_config: Optional[Dict[str, Any]] = None,
        api_config: Optional[Dict[str, Any]] = None,
    ) -> SecurityOperationsResult:
        """Runs complete end-to-end security operations & compliance evaluation."""

        now_str = datetime.now(timezone.utc).isoformat()

        # Step 1: Audit Log initial action
        self.audit_logger.log_event(
            event_type="SECURITY_ASSESSMENT_STARTED",
            severity="INFO",
            description=f"Starting security assessment for {target_name}",
            actor="SecurityOperationsOrchestrator",
            resource_id=target_name,
            metadata={"is_production": is_production},
        )

        # Step 2: Posture Evaluation
        posture_res = self.posture_evaluator.evaluate(
            env_config=env_config,
            package_manifest=package_manifest,
            container_config=container_config,
            auth_config=auth_config,
            authz_config=authz_config,
            api_config=api_config,
            is_production=is_production,
        )

        # Step 3: Policy Evaluation
        policy_res = self.policy_engine.evaluate_policy(
            posture_result=posture_res,
            is_production=is_production,
        )

        # Step 4: Compliance Evaluation
        compliance_res = self.compliance_engine.evaluate(
            posture_result=posture_res,
            is_production=is_production,
        )

        # Step 5: Risk Evaluation
        vulnerabilities = (
            posture_res.vulnerability_assessment.vulnerabilities if posture_res.vulnerability_assessment else []
        )

        active_exceptions = self.exception_manager.get_active_exceptions()
        risk_res = self.risk_engine.assess_risk(
            posture_score=posture_res.score,
            vulnerabilities=vulnerabilities,
            active_exceptions=active_exceptions,
            is_production=is_production,
        )

        # Step 6: Audit Integrity Check
        audit_integrity_res = self.audit_integrity_engine.validate_audit_chain()

        # Step 7: Certification
        cert_res = self.certification_engine.certify(
            posture_result=posture_res,
            policy_result=policy_res,
            compliance_result=compliance_res,
            risk_assessment=risk_res,
            audit_integrity=audit_integrity_res,
            is_production=is_production,
        )

        # Step 8: Metrics Calculation
        metrics_res = self.metrics_calculator.calculate_metrics(
            posture_score=posture_res.score,
            vulnerability_assessment=posture_res.vulnerability_assessment,
            active_exceptions_count=len(active_exceptions),
            compliance_score=compliance_res.overall_compliance_score,
            is_production=is_production,
        )

        # Step 9: Dashboard Snapshot
        dashboard_snap = self.dashboard.generate_snapshot(
            posture_result=posture_res,
            metrics_result=metrics_res,
            risk_assessment=risk_res,
            compliance_result=compliance_res,
            audit_integrity=audit_integrity_res,
            certification_result=cert_res,
            active_exceptions_count=len(active_exceptions),
            active_threats_count=0,
            is_production=is_production,
        )

        # Step 10: Evidence Collection
        evidence_obj = self.evidence_collector.collect_evidence(
            posture_result=posture_res,
            policy_result=policy_res,
            compliance_result=compliance_res,
            risk_assessment=risk_res,
            certification_result=cert_res,
            is_production=is_production,
        )

        # Audit log completion
        self.audit_logger.log_event(
            event_type="SECURITY_ASSESSMENT_COMPLETED",
            severity="INFO" if cert_res.is_certified else "WARNING",
            description=f"Security assessment completed. Decision: {cert_res.decision}",
            actor="SecurityOperationsOrchestrator",
            resource_id=target_name,
            metadata={
                "is_certified": cert_res.is_certified,
                "decision": cert_res.decision,
                "score": posture_res.score,
                "is_production": is_production,
            },
        )

        # Fingerprint calculation
        payload_for_fp = {
            "target": target_name,
            "cert": cert_res.decision,
            "score": posture_res.score,
            "evidence_fp": evidence_obj.fingerprint,
            "is_prod": is_production,
        }
        fp_hash = hashlib.sha256(json.dumps(payload_for_fp, sort_keys=True).encode("utf-8")).hexdigest()
        fingerprint = f"sha256:{fp_hash}"

        return SecurityOperationsResult(
            timestamp=now_str,
            is_certified=cert_res.is_certified,
            certification_decision=cert_res.decision,
            posture_score=posture_res.score,
            posture_status=posture_res.status,
            policy_action=policy_res.action,
            risk_level=risk_res.overall_risk_level,
            compliance_score=compliance_res.overall_compliance_score,
            audit_integrity_passed=audit_integrity_res.is_valid,
            is_production=is_production,
            unexecuted_claims=cert_res.unexecuted_claims,
            posture_result=posture_res,
            policy_result=policy_res,
            compliance_result=compliance_res,
            risk_assessment=risk_res,
            certification_result=cert_res,
            metrics_result=metrics_res,
            dashboard_snapshot=dashboard_snap,
            evidence=evidence_obj,
            fingerprint=fingerprint,
            metadata={
                "sanitized": True,
                "orchestrator_version": "5.69.0",
            },
        )
