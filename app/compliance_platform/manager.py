"""Master CompliancePlatformManager Orchestrator Subsystem."""

import logging
from typing import Any, Dict

from app.compliance_platform.analytics import ComplianceAnalyticsEngine
from app.compliance_platform.assessments import AssessmentResult, ComplianceAssessmentManager
from app.compliance_platform.assurance import AssuranceConclusion, AssuranceManager
from app.compliance_platform.attestations import AttestationManager
from app.compliance_platform.audit import AuditManager
from app.compliance_platform.billing import ComplianceBillingTracker
from app.compliance_platform.collection import EvidenceCollectionManager
from app.compliance_platform.continuous_monitoring import ComplianceMonitoringManager
from app.compliance_platform.controls import ControlCategory, ControlImplementation, ControlManager, ControlType
from app.compliance_platform.evidence import EvidenceManager, EvidenceType
from app.compliance_platform.exceptions_management import ExceptionManager
from app.compliance_platform.findings import FindingManager
from app.compliance_platform.frameworks import FrameworkManager, FrameworkType
from app.compliance_platform.governance import ComplianceGovernanceEngine
from app.compliance_platform.mappings import MappingManager
from app.compliance_platform.observability import ComplianceMetricsCollector
from app.compliance_platform.posture import CompliancePostureManager
from app.compliance_platform.remediation import ComplianceRemediationManager
from app.compliance_platform.repositories import ComplianceRepository
from app.compliance_platform.requirements import RequirementManager, RequirementScope
from app.compliance_platform.trust import ComplianceTrustEngine

logger = logging.getLogger(__name__)


class CompliancePlatformManager:
    """Master Orchestrator unifying all 23 Compliance Platform domain subsystems."""

    def __init__(self) -> None:
        self.repository = ComplianceRepository()

        self.framework_manager = FrameworkManager()
        self.requirement_manager = RequirementManager()
        self.control_manager = ControlManager()
        self.mapping_manager = MappingManager(
            requirement_manager=self.requirement_manager,
            control_manager=self.control_manager,
        )

        self.evidence_manager = EvidenceManager()
        self.collection_manager = EvidenceCollectionManager(evidence_manager=self.evidence_manager)

        self.assessment_manager = ComplianceAssessmentManager(
            framework_manager=self.framework_manager,
            requirement_manager=self.requirement_manager,
            control_manager=self.control_manager,
            evidence_manager=self.evidence_manager,
        )

        self.finding_manager = FindingManager()
        self.governance_engine = ComplianceGovernanceEngine()
        self.remediation_manager = ComplianceRemediationManager(approval_engine=self.governance_engine.approval_engine)

        self.attestation_manager = AttestationManager()
        self.exception_manager = ExceptionManager()
        self.monitoring_manager = ComplianceMonitoringManager()

        self.posture_manager = CompliancePostureManager()
        self.assurance_manager = AssuranceManager()
        self.audit_manager = AuditManager()
        self.trust_engine = ComplianceTrustEngine()

        self.metrics_collector = ComplianceMetricsCollector()
        self.analytics_engine = ComplianceAnalyticsEngine(
            framework_manager=self.framework_manager,
            control_manager=self.control_manager,
            finding_manager=self.finding_manager,
            posture_manager=self.posture_manager,
        )
        self.billing_tracker = ComplianceBillingTracker()

        logger.info("[COMPLIANCE MASTER] CompliancePlatformManager initialized cleanly with all 23 domain subsystems.")

    def run_full_compliance_flow(
        self,
        tenant_id: str,
        framework_type: FrameworkType = FrameworkType.SOC_2,
        subject_id: str = "global",
    ) -> Dict[str, Any]:
        """Runs complete compliance flow: Framework Adoption -> Requirement -> Control -> Evidence -> Assessment -> Posture -> Report."""
        # 1. Framework & Requirements
        fw = self.framework_manager.adopt_framework(
            tenant_id=tenant_id,
            framework_type=framework_type,
            name=f"{framework_type.value} Framework",
            description="Compliance Framework",
        )
        req = self.requirement_manager.register_requirement(
            tenant_id=tenant_id,
            framework_id=fw.framework_id,
            code=f"{framework_type.value}-01",
            title="Access Control Security",
            description="Ensure access controls are active.",
            scope=RequirementScope.TENANT,
        )

        # 2. Control & Mapping
        impl = ControlImplementation(source_subsystem="IdentitySecurityManager", method_name="verify_access")
        ctrl = self.control_manager.register_control(
            tenant_id=tenant_id,
            code="CTRL-ACC-01",
            name="Access Verification Control",
            description="Control verifying user identity.",
            control_type=ControlType.PREVENTIVE,
            category=ControlCategory.ACCESS,
            implementation=impl,
            requirement_ids=[req.requirement_id],
        )
        self.mapping_manager.map_requirement_to_control(tenant_id, req.requirement_id, ctrl.control_id)

        # 3. Evidence Collection
        col_res = self.collection_manager.collect_evidence_for_subject(
            tenant_id=tenant_id,
            idempotency_key=f"flow_idemp_{tenant_id}_{fw.framework_id}",
            subject_type="TENANT",
            subject_id=subject_id,
            required_types=[EvidenceType.IDENTITY_EVENT],
        )

        # 4. Assessment
        assessment = self.assessment_manager.run_assessment(tenant_id, fw.framework_id, subject_id=subject_id)
        self.metrics_collector.increment("ai_compliance_assessments_total")

        # 5. Posture & Assurance Report
        posture = self.posture_manager.calculate_posture(tenant_id)
        report = self.assurance_manager.generate_assurance_report(
            tenant_id=tenant_id,
            framework_id=fw.framework_id,
            conclusion=(
                AssuranceConclusion.ASSURED
                if assessment.overall_result == AssessmentResult.PASS
                else AssuranceConclusion.INSUFFICIENT_EVIDENCE
            ),
        )
        self.metrics_collector.increment("ai_compliance_assurance_reports_total")

        return {
            "framework": fw.model_dump(),
            "requirement": req.model_dump(),
            "control": ctrl.model_dump(),
            "evidence_collection": col_res.model_dump(),
            "assessment": assessment.model_dump(),
            "posture": posture.model_dump(),
            "assurance_report": report.model_dump(),
        }

    def get_summary(self, tenant_id: str = "global") -> Dict[str, Any]:
        """Aggregate master summary for control plane and CLI."""
        report = self.analytics_engine.generate_report(tenant_id)
        metrics = self.metrics_collector.get_metrics_summary()
        return {
            "status": "OPERATIONAL",
            "report": report.model_dump(),
            "metrics": metrics,
        }
