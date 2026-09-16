"""
Security Operations, Compliance Governance, Audit Assurance & Continuous Security Certification package for Enterprise AI Platform.
Phase 5.69 canonical security operations module.
"""

from app.security_operations.api_security import APISecurityEvaluator, APISecurityResult
from app.security_operations.audit_integrity import AuditIntegrityEngine, AuditIntegrityResult
from app.security_operations.audit_log import AuditIntegrityValidator, SecurityAuditLogger, SecurityAuditRecord
from app.security_operations.authentication_security import (
    AuthenticationSecurityEvaluator,
    AuthenticationSecurityResult,
)
from app.security_operations.authorization_security import AuthorizationSecurityEvaluator, AuthorizationSecurityResult
from app.security_operations.compliance_governance import (
    ComplianceFramework,
    ComplianceGovernanceEngine,
    ComplianceRequirement,
    ComplianceResult,
)
from app.security_operations.container_security import ContainerSecurityEvaluator, ContainerSecurityResult
from app.security_operations.dependency_security import (
    DependencyRisk,
    DependencySecurityEvaluator,
    DependencySecurityResult,
)
from app.security_operations.secret_security import SecretSecurityEvaluator, SecretSecurityResult
from app.security_operations.security_certification import (
    SecurityCertificationDecision,
    SecurityCertificationEngine,
    SecurityCertificationResult,
)
from app.security_operations.security_dashboard import SecurityDashboardSnapshot
from app.security_operations.security_event_detection import SecurityEvent, SecurityEventDetector, SecurityEventType
from app.security_operations.security_evidence import SecurityEvidence, SecurityEvidenceCollector, SecurityEvidenceLevel
from app.security_operations.security_exception_management import (
    SecurityException,
    SecurityExceptionManager,
    SecurityExceptionStatus,
)
from app.security_operations.security_metrics import SecurityMetricsCalculator, SecurityMetricsResult
from app.security_operations.security_operations_orchestrator import (
    SecurityOperationsOrchestrator,
    SecurityOperationsResult,
)
from app.security_operations.security_policy_engine import (
    SecurityPolicy,
    SecurityPolicyEngine,
    SecurityPolicyResult,
    SecurityPolicyRule,
)
from app.security_operations.security_posture import SecurityPosture, SecurityPostureEvaluator, SecurityPostureResult
from app.security_operations.security_risk_engine import RiskAssessment, SecurityRisk, SecurityRiskEngine
from app.security_operations.security_threat_classifier import SecurityThreat, SecurityThreatClassifier, ThreatSeverity
from app.security_operations.vulnerability_management import (
    Vulnerability,
    VulnerabilityAssessment,
    VulnerabilityManager,
    VulnerabilitySeverity,
)

__all__ = [
    "SecurityPostureEvaluator",
    "SecurityPosture",
    "SecurityPostureResult",
    "SecurityPolicyEngine",
    "SecurityPolicy",
    "SecurityPolicyRule",
    "SecurityPolicyResult",
    "VulnerabilityManager",
    "Vulnerability",
    "VulnerabilitySeverity",
    "VulnerabilityAssessment",
    "DependencySecurityEvaluator",
    "DependencySecurityResult",
    "DependencyRisk",
    "ContainerSecurityEvaluator",
    "ContainerSecurityResult",
    "SecretSecurityEvaluator",
    "SecretSecurityResult",
    "AuthenticationSecurityEvaluator",
    "AuthenticationSecurityResult",
    "AuthorizationSecurityEvaluator",
    "AuthorizationSecurityResult",
    "APISecurityEvaluator",
    "APISecurityResult",
    "SecurityEventDetector",
    "SecurityEvent",
    "SecurityEventType",
    "SecurityThreatClassifier",
    "SecurityThreat",
    "ThreatSeverity",
    "ComplianceGovernanceEngine",
    "ComplianceFramework",
    "ComplianceRequirement",
    "ComplianceResult",
    "SecurityAuditLogger",
    "SecurityAuditRecord",
    "AuditIntegrityValidator",
    "AuditIntegrityEngine",
    "AuditIntegrityResult",
    "SecurityRiskEngine",
    "SecurityRisk",
    "RiskAssessment",
    "SecurityExceptionManager",
    "SecurityException",
    "SecurityExceptionStatus",
    "SecurityEvidenceCollector",
    "SecurityEvidence",
    "SecurityEvidenceLevel",
    "SecurityCertificationEngine",
    "SecurityCertificationResult",
    "SecurityCertificationDecision",
    "SecurityOperationsOrchestrator",
    "SecurityOperationsResult",
    "SecurityMetricsCalculator",
    "SecurityMetricsResult",
    "SecurityDashboardSnapshot",
]
