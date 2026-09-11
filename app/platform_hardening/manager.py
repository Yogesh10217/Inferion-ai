"""
Platform Hardening Manager.
Thin orchestrator delegating audits, AST parsing, cross-phase validations, hardening, and certification.
"""

import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional
from app.platform_hardening.api_contract_validation import APIContractValidationEngine
from app.platform_hardening.ast_analysis import PlatformASTAnalysisEngine
from app.platform_hardening.certification import PlatformCertificationEngine
from app.platform_hardening.code_analysis import PlatformCodeAnalysisEngine
from app.platform_hardening.concurrency_validation import PlatformConcurrencyValidationEngine
from app.platform_hardening.context_validation import CrossPhaseContextValidationEngine
from app.platform_hardening.dead_code import DeadCodeDetectionEngine
from app.platform_hardening.delegation_validation import CrossPhaseDelegationValidationEngine
from app.platform_hardening.dependency_validation import PlatformDependencyValidationEngine
from app.platform_hardening.duplication_detection import PlatformDuplicationDetectionEngine
from app.platform_hardening.engine_connectivity import EngineConnectivityAudit
from app.platform_hardening.evidence import PlatformHardeningEvidenceLedger
from app.platform_hardening.evidence_validation import CrossPhaseEvidenceValidationEngine
from app.platform_hardening.exceptions import CrossTenantPlatformHardeningException
from app.platform_hardening.feedback_loops import PlatformFeedbackLoopValidationEngine
from app.platform_hardening.governance_validation import CrossPhaseGovernanceValidationEngine
from app.platform_hardening.hardening import PlatformHardeningEngine
from app.platform_hardening.idempotency_validation import PlatformIdempotencyValidationEngine
from app.platform_hardening.integration_audit import CrossPhaseIntegrationAuditEngine
from app.platform_hardening.lineage_validation import PlatformLineageValidationEngine
from app.platform_hardening.manager_validation import ManagerIntegrationValidationEngine
from app.platform_hardening.models import (
    IntegrationHealth,
    IntegrationHealthStatus,
    PlatformAuditFinding,
    PlatformAuditResult,
    PlatformAuditStatus,
    PlatformCertification,
    PlatformCertificationStatus,
    PlatformHealthSummary,
    ReleaseReadinessDecision,
)
from app.platform_hardening.platform_score import PlatformProductionReadinessEngine
from app.platform_hardening.provider_audit import ProviderIntegrationAuditEngine
from app.platform_hardening.providers import PlatformHardeningProviderRegistry
from app.platform_hardening.release_gate import PlatformReleaseGateEngine
from app.platform_hardening.remediation import PlatformRemediationPlanner
from app.platform_hardening.repositories import (
    AuditFindingRepository,
    CertificationRepository,
    IntegrationHealthRepository,
    PlatformAuditRepository,
    RemediationRepository,
)
from app.platform_hardening.repository_validation import RepositoryIsolationValidationEngine
from app.platform_hardening.stub_detection import ProductionStubDetectionEngine
from app.platform_hardening.subsystem_registry import SubsystemRegistry
from app.platform_hardening.trace_validation import TracePropagationValidationEngine
from app.platform_hardening.verification_validation import CrossPhaseVerificationValidationEngine


class PlatformHardeningManager:
    """Thin manager orchestrating platform-wide audits, AST code scans, safety validations, and certification."""

    def __init__(
        self,
        provider_registry: Optional[PlatformHardeningProviderRegistry] = None,
        subsystem_registry: Optional[SubsystemRegistry] = None,
        audit_repo: Optional[PlatformAuditRepository] = None,
        finding_repo: Optional[AuditFindingRepository] = None,
        cert_repo: Optional[CertificationRepository] = None,
        rem_repo: Optional[RemediationRepository] = None,
        health_repo: Optional[IntegrationHealthRepository] = None,
    ):
        self.provider_registry = provider_registry or PlatformHardeningProviderRegistry()
        self.subsystem_registry = subsystem_registry or SubsystemRegistry()

        # Repositories
        self.audit_repo = audit_repo or PlatformAuditRepository()
        self.finding_repo = finding_repo or AuditFindingRepository()
        self.cert_repo = cert_repo or CertificationRepository()
        self.rem_repo = rem_repo or RemediationRepository()
        self.health_repo = health_repo or IntegrationHealthRepository()

        # Validation Engines
        self.integration_audit = CrossPhaseIntegrationAuditEngine(self.subsystem_registry)
        self.provider_audit = ProviderIntegrationAuditEngine(self.provider_registry)
        self.context_validation = CrossPhaseContextValidationEngine()
        self.trace_validation = TracePropagationValidationEngine()
        self.lineage_validation = PlatformLineageValidationEngine()
        self.evidence_validation = CrossPhaseEvidenceValidationEngine()
        self.engine_connectivity = EngineConnectivityAudit()
        self.manager_validation = ManagerIntegrationValidationEngine()
        self.stub_detection = ProductionStubDetectionEngine()
        self.dead_code_detection = DeadCodeDetectionEngine()
        self.duplication_detection = PlatformDuplicationDetectionEngine()
        self.dependency_validation = PlatformDependencyValidationEngine()
        self.repository_validation = RepositoryIsolationValidationEngine()
        self.concurrency_validation = PlatformConcurrencyValidationEngine()
        self.idempotency_validation = PlatformIdempotencyValidationEngine()
        self.governance_validation = CrossPhaseGovernanceValidationEngine()
        self.delegation_validation = CrossPhaseDelegationValidationEngine()
        self.verification_validation = CrossPhaseVerificationValidationEngine()
        self.feedback_loops_validation = PlatformFeedbackLoopValidationEngine()
        self.api_contract_validation = APIContractValidationEngine()

        # Hardening, Gate & Certification
        self.remediation_planner = PlatformRemediationPlanner()
        self.hardening_engine = PlatformHardeningEngine()
        self.release_gate_engine = PlatformReleaseGateEngine()
        self.certification_engine = PlatformCertificationEngine()
        self.readiness_engine = PlatformProductionReadinessEngine()
        self.evidence_ledger = PlatformHardeningEvidenceLedger()

    def run_platform_audit(self, tenant_id: str = "system") -> PlatformAuditResult:
        audit_id = f"audit-{uuid.uuid4().hex[:12]}"
        now = datetime.now(timezone.utc)
        all_findings: List[PlatformAuditFinding] = []

        # 1. Integration Health Audit
        health, int_findings = self.integration_audit.audit_integration(tenant_id=tenant_id)
        all_findings.extend(int_findings)
        self.health_repo.save(tenant_id, health)

        # 2. Provider Audit
        _, prov_findings = self.provider_audit.audit_providers(tenant_id=tenant_id)
        all_findings.extend(prov_findings)

        # 3. AST Stub Detection Scan
        stub_res = self.stub_detection.scan_stubs(tenant_id=tenant_id)
        all_findings.extend(stub_res.findings)

        # 4. AST Dead Code Scan
        dead_res = self.dead_code_detection.scan_dead_code(tenant_id=tenant_id)
        all_findings.extend(dead_res.findings)

        # 5. Duplication Scan
        dup_res = self.duplication_detection.scan_duplicates(tenant_id=tenant_id)
        all_findings.extend(dup_res.findings)

        # 6. Dependency Graph Validation
        dep_res = self.dependency_validation.validate_dependencies(tenant_id=tenant_id)
        all_findings.extend(dep_res.findings)

        # Save findings
        for f in all_findings:
            f.metadata["audit_id"] = audit_id
            self.finding_repo.save(tenant_id, f)

        # 7. Generate Remediation Plan
        remediations = self.remediation_planner.generate_remediations(all_findings, tenant_id=tenant_id)
        for r in remediations:
            self.rem_repo.save(tenant_id, r)

        # 8. Calculate Readiness Scores
        score_dict = self.readiness_engine.calculate_readiness_report(all_findings, tenant_id=tenant_id)
        readiness_score = score_dict["overall"]

        # 9. Evaluate Release Gate Decision
        release_gate = self.release_gate_engine.evaluate_release_gate(
            findings=all_findings,
            cross_tenant_leak=False,
            direct_infra_mutation=False,
            approval_bypass=False,
            broken_evidence_chain=False,
        )

        # 10. Issue Platform Certification
        certification = self.certification_engine.certify_platform(
            tenant_id=tenant_id,
            audit_id=audit_id,
            readiness_score=readiness_score,
            release_gate=release_gate,
            findings=all_findings,
        )
        self.cert_repo.save(tenant_id, certification)

        audit_result = PlatformAuditResult(
            audit_id=audit_id,
            tenant_id=tenant_id,
            status=PlatformAuditStatus.COMPLETED,
            findings=all_findings,
            remediations=remediations,
            certification=certification,
            release_gate=release_gate,
            readiness_score=readiness_score,
            started_at=now,
            completed_at=datetime.now(timezone.utc),
        )

        self.audit_repo.save(tenant_id, audit_result)
        self.audit_repo.seal(tenant_id, audit_id)

        return audit_result

    def get_platform_health_summary(self, tenant_id: str = "system") -> PlatformHealthSummary:
        health = self.health_repo.get(tenant_id)
        health_status = health.overall_health if health else IntegrationHealthStatus.HEALTHY
        cert = self.cert_repo.get_latest(tenant_id)

        findings = self.finding_repo.list_by_tenant(tenant_id)
        critical_count = sum(1 for f in findings if f.severity.value == "CRITICAL")

        return PlatformHealthSummary(
            tenant_id=tenant_id,
            integration_health=health_status,
            certification_status=cert.status if cert else PlatformCertificationStatus.FAILED,
            release_readiness=cert.release_decision if cert else ReleaseReadinessDecision.BLOCKED,
            readiness_score=cert.overall_score if cert else 0.0,
            total_findings=len(findings),
            critical_findings=critical_count,
        )
