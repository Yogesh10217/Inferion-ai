"""Master Orchestrator for Operations Intelligence Platform (Phase 5.41)."""

from typing import Dict, Any, Optional, List

from app.operations_intelligence.services import OperationalServiceManager, ServiceCriticality, ServiceOperationalTier, ServiceHealthStatus
from app.operations_intelligence.incidents import IncidentManager, IncidentSeverity, IncidentPriority, IncidentStatus
from app.operations_intelligence.major_incidents import MajorIncidentManager, MajorIncidentImpact
from app.operations_intelligence.alerts import AlertManager, AlertSeverity
from app.operations_intelligence.correlation import CorrelationManager, CorrelationEvidence
from app.operations_intelligence.root_cause import RootCauseManager, RootCauseHypothesis, RootCauseEvidence, RootCauseConfidence
from app.operations_intelligence.problems import ProblemManager
from app.operations_intelligence.known_errors import KnownErrorManager
from app.operations_intelligence.changes import ChangeIntelligenceManager, ChangeRisk, ChangeImpact
from app.operations_intelligence.change_risk import ChangeRiskManager
from app.operations_intelligence.impact import ImpactAnalysisManager, BusinessImpact, TechnicalImpact
from app.operations_intelligence.dependencies import OperationalDependencyManager, DependencyImpact
from app.operations_intelligence.runbooks import OperationalRunbookManager
from app.operations_intelligence.remediation import OperationalRemediationManager, RemediationAction, RemediationPriority
from app.operations_intelligence.automation import OperationalAutomationManager
from app.operations_intelligence.investigations import OperationalInvestigationManager
from app.operations_intelligence.communications import CommunicationManager, CommunicationAudience
from app.operations_intelligence.sla import ServiceObjectiveManager
from app.operations_intelligence.governance import OperationsGovernanceEngine, OperationsGovernanceStatus
from app.operations_intelligence.delegation import OperationalDelegationManager
from app.operations_intelligence.verification import OperationsVerificationManager
from app.operations_intelligence.evidence import OperationalEvidenceManager
from app.operations_intelligence.snapshots import OperationalSnapshotManager
from app.operations_intelligence.trust import OperationalTrustEngine
from app.operations_intelligence.learning import OperationalLearningManager
from app.operations_intelligence.analytics import OperationsAnalyticsEngine
from app.operations_intelligence.observability import OperationsMetricsCollector
from app.operations_intelligence.billing import OperationsBillingTracker
from app.operations_intelligence.repositories import (
    ServiceRepository,
    IncidentRepository,
    MajorIncidentRepository,
    AlertRepository,
    ProblemRepository,
    KnownErrorRepository,
    InvestigationRepository,
)


class OperationsIntelligenceManager:
    """Master orchestrator for Enterprise AI Operations Intelligence Platform."""

    def __init__(self) -> None:
        self.service_manager = OperationalServiceManager()
        self.incident_manager = IncidentManager()
        self.major_incident_manager = MajorIncidentManager()
        self.alert_manager = AlertManager()
        self.correlation_manager = CorrelationManager()
        self.root_cause_manager = RootCauseManager()
        self.problem_manager = ProblemManager()
        self.known_error_manager = KnownErrorManager()
        self.change_manager = ChangeIntelligenceManager()
        self.change_risk_manager = ChangeRiskManager()
        self.impact_manager = ImpactAnalysisManager()
        self.dependency_manager = OperationalDependencyManager()
        self.runbook_manager = OperationalRunbookManager()
        self.remediation_manager = OperationalRemediationManager()
        self.automation_manager = OperationalAutomationManager()
        self.investigation_manager = OperationalInvestigationManager()
        self.communication_manager = CommunicationManager()
        self.slo_manager = ServiceObjectiveManager()
        self.governance_engine = OperationsGovernanceEngine()
        self.delegation_manager = OperationalDelegationManager()
        self.verification_manager = OperationsVerificationManager()
        self.evidence_manager = OperationalEvidenceManager()
        self.snapshot_manager = OperationalSnapshotManager()
        self.trust_engine = OperationalTrustEngine()
        self.learning_manager = OperationalLearningManager()
        self.analytics_engine = OperationsAnalyticsEngine()
        self.metrics_collector = OperationsMetricsCollector()
        self.billing_tracker = OperationsBillingTracker()

        # Repositories
        self.service_repo = ServiceRepository()
        self.incident_repo = IncidentRepository()
        self.major_incident_repo = MajorIncidentRepository()
        self.alert_repo = AlertRepository()
        self.problem_repo = ProblemRepository()
        self.known_error_repo = KnownErrorRepository()
        self.investigation_repo = InvestigationRepository()

    def run_full_lifecycle(
        self,
        tenant_id: str,
        service_name: str,
        incident_title: str,
        idempotency_key: str = "idem_ops_full_100",
    ) -> Dict[str, Any]:
        """Runs the complete end-to-end governed operational lifecycle."""
        # 1. Service Registration
        svc = self.service_manager.register_service(tenant_id, service_name, "PlatformSRE")
        self.service_repo.save(svc)

        # 2. Ingest Alert
        alert = self.alert_manager.ingest_alert(tenant_id, "Prometheus", svc.service_id, "LatencySpike", f"fp_{service_name}_lat")
        self.alert_repo.save(alert)
        self.metrics_collector.increment("alerts_ingested_total")

        # 3. Create Incident
        inc = self.incident_manager.create_incident(tenant_id, incident_title, svc.service_id)
        self.incident_repo.save(inc)
        self.metrics_collector.increment("incidents_created_total")

        # 4. Correlate Events
        corr_ev = CorrelationEvidence(event_source="ALERTS", event_id=alert.alert_id, summary="High latency detected")
        corr = self.correlation_manager.correlate_events(tenant_id, inc.incident_id, [corr_ev])

        # 5. Open Investigation
        inv = self.investigation_manager.open_investigation(tenant_id, f"Investigation: {incident_title}", inc.incident_id)
        self.investigation_manager.start_investigating(tenant_id, inv.investigation_id)
        self.investigation_manager.record_finding(tenant_id, inv.investigation_id, "High CPU memory pressure")

        # 6. Root Cause Analysis
        hypo = RootCauseHypothesis(title="Memory Leak in Worker", component_name=svc.name, likelihood_score=90.0, reasoning="Garbage collection pressure")
        ev = RootCauseEvidence(source="METRICS", description="Heap usage at 98%")
        rca = self.root_cause_manager.analyze_root_cause(tenant_id, inc.incident_id, "Memory leak in worker thread pool", [hypo], [ev])
        self.investigation_manager.set_root_cause_analyzed(tenant_id, inv.investigation_id, rca.analysis_id)

        # 7. Problem Creation & Known Error
        prob = self.problem_manager.create_problem(tenant_id, f"Problem: {incident_title}", [inc.incident_id])
        self.problem_manager.set_root_cause(tenant_id, prob.problem_id, rca.analysis_id)
        self.problem_repo.save(prob)

        ke = self.known_error_manager.publish_known_error(tenant_id, f"Known Error: {incident_title}", "Restart worker pool process", prob.problem_id)
        self.known_error_repo.save(ke)

        # 8. Remediation Planning & Governance
        action = RemediationAction(action_name="RESTART_SERVICE", target_service_id=svc.service_id, is_high_risk=False)
        rem_plan = self.remediation_manager.create_remediation_plan(tenant_id, inc.incident_id, idempotency_key, [action])

        gov_dec = self.governance_engine.evaluate_governance(tenant_id, "RESTART_SERVICE", risk_score=20.0)
        del_req = self.remediation_manager.delegate_remediation(tenant_id, rem_plan.plan_id)
        self.metrics_collector.increment("remediations_delegated_total")

        # 9. Verification & Resolution
        verif = self.verification_manager.verify_remediation(tenant_id, rem_plan.plan_id, service_recovered=True)
        self.incident_manager.resolve_incident(tenant_id, inc.incident_id)

        # 10. Conclude Investigation & Capture Snapshot
        concluded_inv = self.investigation_manager.conclude_investigation(tenant_id, inv.investigation_id)
        self.investigation_repo.save(concluded_inv)
        snap = self.snapshot_manager.capture_snapshot(tenant_id, concluded_inv.investigation_id, "OPERATIONAL_INVESTIGATION", concluded_inv.model_dump(mode="json"))

        # 11. Evidence Bundle Finalization
        bundle = self.evidence_manager.create_bundle(tenant_id, f"Evidence for {incident_title}")
        self.evidence_manager.add_evidence(tenant_id, bundle.bundle_id, "ALERT_LOG", alert.alert_id, {"raw": "alert data"})
        finalized_bundle = self.evidence_manager.finalize_bundle(tenant_id, bundle.bundle_id)

        # 12. Learning Recommendation
        learning = self.learning_manager.record_learning(
            tenant_id=tenant_id,
            pattern_name="WorkerMemoryLeakPattern",
            description="Worker memory pressure under peak load",
            recommendation_title="Increase heap limit",
            suggested_action="Adjust heap limit configuration",
            target_service_id=svc.service_id,
        )

        # 13. Billing & Analytics
        self.billing_tracker.record_cost(tenant_id, "FULL_LIFECYCLE_TRIAGE", 0.05)
        report = self.analytics_engine.generate_report(tenant_id, active_services_count=1, open_incidents_count=0, mttr_minutes=12.0)

        return {
            "status": "COMPLETED",
            "service_id": svc.service_id,
            "incident_id": inc.incident_id,
            "delegation_id": del_req.delegation_id,
            "governance_status": gov_dec.status.value,
            "snapshot_id": snap.snapshot_id,
            "evidence_sha256": finalized_bundle.sha256_hash,
            "learning_auto_execute": learning.recommendations[0].auto_execute,
        }
