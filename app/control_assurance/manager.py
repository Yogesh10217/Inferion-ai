"""Master ControlAssuranceManager Orchestrator Subsystem (Phase 5.38)."""

import logging
from typing import Any, Dict

from app.control_assurance.analytics import ControlAssuranceAnalyticsEngine
from app.control_assurance.assurance import AssuranceDimension, AssuranceFinding, AssuranceManager
from app.control_assurance.attestation import ControlAttestationManager
from app.control_assurance.audit import ControlAssuranceAuditManager
from app.control_assurance.billing import ControlAssuranceBillingTracker
from app.control_assurance.continuous_monitoring import ContinuousMonitoringManager
from app.control_assurance.controls import ControlCategory, ControlCriticality, ControlManager
from app.control_assurance.correlation import ControlCorrelationManager
from app.control_assurance.delegation import ControlDelegationManager
from app.control_assurance.evaluation import ControlEvaluationManager
from app.control_assurance.evidence import ControlEvidenceManager
from app.control_assurance.exceptions_management import ControlExceptionManager
from app.control_assurance.frameworks import ControlFrameworkManager
from app.control_assurance.governance import ControlGovernanceEngine
from app.control_assurance.impact import ControlImpactAnalyzer
from app.control_assurance.learning import ControlLearningManager
from app.control_assurance.observability import ControlAssuranceMetricsCollector
from app.control_assurance.policy_intelligence import PolicyIntelligenceManager
from app.control_assurance.remediation import ControlRemediationManager
from app.control_assurance.repositories import ControlAssuranceRepository
from app.control_assurance.risk import ControlRiskManager
from app.control_assurance.scope import ControlScopeResolver, ScopeTarget
from app.control_assurance.signals import (
    ControlSignalManager,
    ControlSignalSeverity,
    ControlSignalSource,
    ControlSignalType,
)
from app.control_assurance.snapshots import ControlAssuranceSnapshotManager
from app.control_assurance.trust import ControlAssuranceTrustEngine
from app.control_assurance.verification import ControlVerificationManager
from app.control_assurance.violations import ControlViolationManager, ViolationSeverity, ViolationStatus
from app.platform_contracts.fingerprinting import FingerprintGenerator
from app.platform_contracts.idempotency import IdempotencyManager
from app.platform_contracts.snapshots import SnapshotFactory
from app.platform_contracts.tenant import TenantAccessGuard

logger = logging.getLogger(__name__)


class ControlAssuranceManager:
    """Master Orchestrator unifying all 30 Control Assurance Subsystems."""

    def __init__(self) -> None:
        self.tenant_guard = TenantAccessGuard()
        self.idempotency_manager = IdempotencyManager()
        self.snapshot_factory = SnapshotFactory()
        self.fingerprint_generator = FingerprintGenerator()

        self.repository = ControlAssuranceRepository(tenant_guard=self.tenant_guard)

        self.control_manager = ControlManager(tenant_guard=self.tenant_guard)
        self.framework_manager = ControlFrameworkManager(tenant_guard=self.tenant_guard)
        self.scope_resolver = ControlScopeResolver(tenant_guard=self.tenant_guard)
        self.signal_manager = ControlSignalManager(tenant_guard=self.tenant_guard)
        self.evaluation_manager = ControlEvaluationManager(tenant_guard=self.tenant_guard)

        self.monitoring_manager = ContinuousMonitoringManager(tenant_guard=self.tenant_guard)
        self.evidence_manager = ControlEvidenceManager(tenant_guard=self.tenant_guard)
        self.violation_manager = ControlViolationManager(tenant_guard=self.tenant_guard)
        self.correlation_manager = ControlCorrelationManager(tenant_guard=self.tenant_guard)
        self.impact_analyzer = ControlImpactAnalyzer(tenant_guard=self.tenant_guard)

        self.risk_manager = ControlRiskManager(tenant_guard=self.tenant_guard)
        self.policy_intelligence_manager = PolicyIntelligenceManager(tenant_guard=self.tenant_guard)
        self.exception_manager = ControlExceptionManager(tenant_guard=self.tenant_guard)
        self.attestation_manager = ControlAttestationManager(tenant_guard=self.tenant_guard)
        self.remediation_manager = ControlRemediationManager(tenant_guard=self.tenant_guard)

        self.verification_manager = ControlVerificationManager(tenant_guard=self.tenant_guard)
        self.assurance_manager = AssuranceManager(tenant_guard=self.tenant_guard)
        self.trust_engine = ControlAssuranceTrustEngine(tenant_guard=self.tenant_guard)
        self.governance_engine = ControlGovernanceEngine(tenant_guard=self.tenant_guard)
        self.delegation_manager = ControlDelegationManager(tenant_guard=self.tenant_guard)

        self.snapshot_manager = ControlAssuranceSnapshotManager(
            snapshot_factory=self.snapshot_factory, tenant_guard=self.tenant_guard
        )
        self.audit_manager = ControlAssuranceAuditManager(tenant_guard=self.tenant_guard)
        self.learning_manager = ControlLearningManager(tenant_guard=self.tenant_guard)

        self.analytics_engine = ControlAssuranceAnalyticsEngine(tenant_guard=self.tenant_guard)
        self.metrics_collector = ControlAssuranceMetricsCollector()
        self.billing_tracker = ControlAssuranceBillingTracker(tenant_guard=self.tenant_guard)

        logger.info("[CONTROL ASSURANCE] ControlAssuranceManager initialized cleanly with all 30 assurance subsystems.")

    def run_full_assurance_lifecycle(
        self,
        tenant_id: str,
        service_id: str = "InferenceEngine_Core",
        force_violation: bool = False,
    ) -> Dict[str, Any]:
        """Executes complete end-to-end 22-step continuous control assurance lifecycle."""

        # 1. Resolve Scope
        scope_res = self.scope_resolver.resolve_scope(tenant_id, ScopeTarget.SERVICE, service_id)

        # 2. Register Control Definition
        ctrl = self.control_manager.register_control(
            tenant_id=tenant_id,
            code="SEC-001",
            name="Enforce Strict API Authentication",
            description="All API requests must contain valid tenant context and authorization token.",
            category=ControlCategory.SECURITY,
            criticality=ControlCriticality.CRITICAL,
        )

        # 3. Resolve Framework & Policy Mappings
        fw = self.framework_manager.create_framework(tenant_id, "SOC2", "SOC2 Trust Services Criteria")
        self.framework_manager.map_control_to_requirement(tenant_id, fw.framework_id, ctrl.control_id, "CC6.1")
        self.policy_intelligence_manager.interpret_control_policy(tenant_id, ctrl.control_id)

        # 4. Collect Signal
        sig = self.signal_manager.collect_signal(
            tenant_id=tenant_id,
            signal_type=ControlSignalType.SECURITY,
            source=ControlSignalSource.SECURITY_INTELLIGENCE,
            source_event_id="evt_sec_001",
            source_resource_id=service_id,
            severity=ControlSignalSeverity.INFO,
            raw_payload={"auth_status": "SUCCESS" if not force_violation else "FAILURE"},
        )

        # 5. Collect & Bundle Evidence
        ev_bundle = self.evidence_manager.create_bundle(tenant_id, ctrl.control_id)
        self.evidence_manager.add_evidence(
            ev_bundle.bundle_id, tenant_id, "SECURITY_SIGNAL", sig.signal_id, sig.sanitized_payload
        )
        fin_bundle = self.evidence_manager.finalize_bundle(ev_bundle.bundle_id, tenant_id)

        # 6. Execute Control Evaluation
        evaluation = self.evaluation_manager.evaluate_control(
            tenant_id=tenant_id,
            control_id=ctrl.control_id,
            scope_target_id=service_id,
            signals=[sig.sanitized_payload],
            force_fail=force_violation,
        )

        # 7. Correlate Findings & Analyze Impact
        self.correlation_manager.correlate_controls(tenant_id, ctrl.control_id, "SEC-002")
        impact = self.impact_analyzer.analyze_impact(tenant_id, ctrl.control_id)

        # 8. Compose Risk & Calculate Assurance Score
        self.risk_manager.assess_control_risk(tenant_id, ctrl.control_id, is_failed=force_violation)
        ass_findings = []
        if force_violation:
            ass_findings.append(
                AssuranceFinding(
                    control_id=ctrl.control_id,
                    dimension=AssuranceDimension.SECURITY,
                    is_hard_failure=True,
                    message="Mandatory security control failure detected.",
                )
            )
        assurance = self.assurance_manager.calculate_assurance(tenant_id, service_id, ass_findings)

        # 9. Handle Violation & Remediation if Failed
        violation_id = None
        plan_id = None
        verif_status = "PASSED"
        if force_violation:
            viol = self.violation_manager.create_violation(
                tenant_id=tenant_id,
                control_id=ctrl.control_id,
                severity=ViolationSeverity.CRITICAL,
                finding_code="SEC-AUTH-01",
                message="Unauthorized request pattern detected",
            )
            violation_id = viol.violation_id

            # Governance evaluation
            self.governance_engine.evaluate_action_governance(tenant_id, "REMEDIATE_CONTROL", ctrl.control_id)

            # Plan delegated remediation
            rem_plan = self.remediation_manager.plan_remediation(tenant_id, viol.violation_id, ctrl.control_id)
            plan_id = rem_plan.plan_id

            # Transition violation status
            self.violation_manager.transition_status(viol.violation_id, tenant_id, ViolationStatus.REMEDIATION_PLANNED)
            self.violation_manager.transition_status(
                viol.violation_id, tenant_id, ViolationStatus.REMEDIATION_DELEGATED
            )

            # Verify remediation
            verif = self.verification_manager.verify_remediation(tenant_id, rem_plan.plan_id, ctrl.control_id)
            verif_status = verif.result.value
            self.violation_manager.transition_status(viol.violation_id, tenant_id, ViolationStatus.VERIFYING)
            self.violation_manager.transition_status(viol.violation_id, tenant_id, ViolationStatus.RESOLVED)
            self.violation_manager.transition_status(viol.violation_id, tenant_id, ViolationStatus.CLOSED)

        # 10. Generate Attestation & Snapshot
        att = self.attestation_manager.create_attestation(tenant_id, ctrl.control_id, service_id)
        fin_att = self.attestation_manager.finalize_attestation(att.attestation_id, tenant_id, "auditor_01")
        snap = self.snapshot_manager.create_snapshot(
            tenant_id, ctrl.control_id, {"status": evaluation.status.value, "score": assurance.assurance_score.score}
        )

        # 11. Trust Engine & Learning Recommendations
        trust = self.trust_engine.calculate_control_trust(tenant_id, ctrl.control_id, is_degraded=force_violation)
        learn = self.learning_manager.record_learning(tenant_id, ctrl.control_id, "Continuous signal stream validated")

        # 12. Audit, Metrics & FinOps Billing
        self.audit_manager.log_event(tenant_id, "CONTROL_EVALUATED", ctrl.control_id)
        self.metrics_collector.increment_evaluations(tenant_id, status=evaluation.status.value)
        self.billing_tracker.record_cost_event(tenant_id, ctrl.control_id, "CONTROL_EVALUATION", 0.01)

        # 13. Analytics Report
        report = self.analytics_engine.generate_assurance_report(tenant_id)

        return {
            "status": "COMPLETED",
            "control_id": ctrl.control_id,
            "evaluation_status": evaluation.status.value,
            "assurance_score": assurance.assurance_score.score,
            "assurance_band": assurance.assurance_score.band.value,
            "evidence_checksum": fin_bundle.checksum_sha256,
            "attestation_fingerprint": fin_att.fingerprint_sha256,
            "snapshot_id": snap.snapshot_id,
            "trust_score": trust.score,
            "violation_id": violation_id,
            "remediation_plan_id": plan_id,
            "verification_status": verif_status,
            "report_id": report.report_id,
        }

    def get_platform_summary(self, tenant_id: str = "global") -> Dict[str, Any]:
        """Aggregate master control assurance platform overview."""
        metrics = self.metrics_collector.get_metrics_summary()
        return {
            "status": "OPERATIONAL",
            "active_controls": len(self.control_manager.list_controls(tenant_id)),
            "metrics": metrics,
        }
