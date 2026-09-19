"""Master Orchestrator for Access Intelligence Platform (Phase 5.39)."""

import logging
from typing import Any, Dict

from app.access_intelligence.access_graph import AccessGraphManager
from app.access_intelligence.access_reviews import AccessReviewManager
from app.access_intelligence.access_risk import AccessRiskManager
from app.access_intelligence.analytics import AccessAnalyticsEngine
from app.access_intelligence.anomalies import AccessAnomalyManager, AccessAnomalyType
from app.access_intelligence.authorization import AuthorizationManager
from app.access_intelligence.billing import AccessBillingTracker
from app.access_intelligence.certifications import AccessCertificationManager
from app.access_intelligence.correlation import AccessCorrelationManager, AccessCorrelationType
from app.access_intelligence.delegation import AccessDelegationManager
from app.access_intelligence.emergency_access import EmergencyAccessManager
from app.access_intelligence.entitlements import EntitlementManager, EntitlementType
from app.access_intelligence.evidence import AccessEvidenceManager
from app.access_intelligence.governance import AccessGovernanceEngine
from app.access_intelligence.identities import IdentityManager, IdentityType
from app.access_intelligence.investigations import AccessInvestigationManager
from app.access_intelligence.learning import AccessLearningManager
from app.access_intelligence.least_privilege import LeastPrivilegeManager
from app.access_intelligence.observability import AccessMetricsCollector
from app.access_intelligence.privileged_access import PrivilegedAccessManager, PrivilegedAccessScope
from app.access_intelligence.relationships import AccessRelationshipManager, AccessRelationshipType
from app.access_intelligence.remediation import AccessRemediationAction, AccessRemediationManager
from app.access_intelligence.signals import AccessSignalManager, AccessSignalType
from app.access_intelligence.snapshots import AccessSnapshotManager
from app.access_intelligence.toxic_combinations import ToxicCombinationManager
from app.access_intelligence.trust import AccessTrustEngine
from app.access_intelligence.verification import AccessVerificationManager, VerificationCheck

logger = logging.getLogger(__name__)


class AccessIntelligenceManager:
    """Master orchestrator unifying all 22 lifecycle capabilities for Enterprise AI Access Intelligence."""

    def __init__(self) -> None:
        self.identity_manager = IdentityManager()
        self.entitlement_manager = EntitlementManager()
        self.relationship_manager = AccessRelationshipManager()
        self.graph_manager = AccessGraphManager()
        self.authorization_manager = AuthorizationManager()
        self.least_privilege_manager = LeastPrivilegeManager()
        self.privileged_access_manager = PrivilegedAccessManager()
        self.emergency_access_manager = EmergencyAccessManager()
        self.risk_manager = AccessRiskManager()
        self.toxic_combination_manager = ToxicCombinationManager()
        self.review_manager = AccessReviewManager()
        self.certification_manager = AccessCertificationManager()
        self.anomaly_manager = AccessAnomalyManager()
        self.signal_manager = AccessSignalManager()
        self.correlation_manager = AccessCorrelationManager()
        self.investigation_manager = AccessInvestigationManager()
        self.remediation_manager = AccessRemediationManager()
        self.governance_engine = AccessGovernanceEngine()
        self.delegation_manager = AccessDelegationManager()
        self.verification_manager = AccessVerificationManager()
        self.evidence_manager = AccessEvidenceManager()
        self.snapshot_manager = AccessSnapshotManager()
        self.trust_engine = AccessTrustEngine()
        self.learning_manager = AccessLearningManager()
        self.analytics_engine = AccessAnalyticsEngine()
        self.metrics_collector = AccessMetricsCollector()
        self.billing_tracker = AccessBillingTracker()

        logger.info("[ACCESS INTELLIGENCE] AccessIntelligenceManager initialized with all 22 lifecycle components.")

    def run_full_lifecycle(self, tenant_id: str, identity_name: str = "agent_executor_01") -> Dict[str, Any]:
        """Runs end-to-end access governance lifecycle workflow without directly mutating external IAM."""
        self.metrics_collector.increment("authorization_requests_total")
        self.billing_tracker.record_cost_event(tenant_id, "FULL_LIFECYCLE_RUN")

        # 1. Identity Reference Registration
        ident = self.identity_manager.register_identity(
            tenant_id=tenant_id,
            name=identity_name,
            identity_type=IdentityType.AGENT,
            external_id=f"ext_{identity_name}",
            provider="internal_iam",
        )

        # 2. Entitlement Discovery
        ent1 = self.entitlement_manager.register_entitlement(
            tenant_id=tenant_id,
            code="READ_KNOWLEDGE",
            name="Read Knowledge Base",
            entitlement_type=EntitlementType.PERMISSION,
            external_entitlement_id="perm_kb_read",
            target_resource_type="KNOWLEDGE_BASE",
            target_resource_id="kb_prod_01",
            action_type="READ",
        )
        ent2 = self.entitlement_manager.register_entitlement(
            tenant_id=tenant_id,
            code="DELETE_RELEASE",
            name="Delete Release",
            entitlement_type=EntitlementType.PERMISSION,
            external_entitlement_id="perm_del_rel",
            target_resource_type="RELEASE",
            target_resource_id="rel_prod_01",
            action_type="DELETE",
            is_privileged=True,
        )

        # 3. Access Relationship Mapping
        rel = self.relationship_manager.create_relationship(
            tenant_id=tenant_id,
            source_identity_id=ident.identity_id,
            target_resource_id="kb_prod_01",
            relationship_type=AccessRelationshipType.AGENT_KNOWLEDGE_ACCESS,
            entitlement_id=ent1.entitlement_id,
        )

        # 4. Access Graph Construction
        self.graph_manager.add_node(tenant_id, ident.identity_id, "IDENTITY", ident.name)
        self.graph_manager.add_node(tenant_id, "kb_prod_01", "SENSITIVE_RESOURCE", "Knowledge Base Prod")
        self.graph_manager.add_edge(tenant_id, ident.identity_id, "kb_prod_01", "AGENT_KNOWLEDGE_ACCESS")

        # 5. Authorization Intelligence Evaluation
        auth_dec = self.authorization_manager.evaluate_authorization(
            tenant_id=tenant_id,
            subject_identity_id=ident.identity_id,
            action="READ",
            resource_id="kb_prod_01",
            resource_type="KNOWLEDGE_BASE",
        )

        # 6. Least Privilege Assessment
        lp_asm = self.least_privilege_manager.assess_identity(
            tenant_id=tenant_id,
            identity_id=ident.identity_id,
            assigned_entitlement_ids=[ent1.entitlement_id, ent2.entitlement_id],
            used_entitlement_ids=[ent1.entitlement_id],
        )

        # 7. Toxic Combination Detection
        tc_findings = self.toxic_combination_manager.evaluate_identity_entitlements(
            tenant_id=tenant_id,
            identity_id=ident.identity_id,
            active_entitlements=["READ_KNOWLEDGE"],
        )

        # 8. Access Risk Assessment
        risk_eval = self.risk_manager.calculate_risk(
            tenant_id=tenant_id,
            subject_identity_id=ident.identity_id,
            resource_id="kb_prod_01",
            privilege_score=20.0,
            resource_sensitivity_score=20.0,
            has_toxic_combinations=len(tc_findings) > 0,
        )

        # 9. Signal and Anomaly Analysis
        sig = self.signal_manager.ingest_signal(
            tenant_id=tenant_id,
            signal_type=AccessSignalType.AUTHORIZATION_EVENT,
            source_telemetry_ref="tel_sig_001",
            subject_identity_id=ident.identity_id,
        )
        anom = self.anomaly_manager.detect_anomaly(
            tenant_id=tenant_id,
            subject_identity_id=ident.identity_id,
            anomaly_type=AccessAnomalyType.UNUSUAL_PRIVILEGE_USAGE,
            title="Unusual Tool Usage",
            description="Agent used privileged tool off-hours.",
            source_signal_id=sig.signal_id,
        )

        # 10. Cross-Platform Correlation
        corr = self.correlation_manager.correlate_event(
            tenant_id=tenant_id,
            correlation_type=AccessCorrelationType.AGENT_EXECUTION_ACCESS,
            subject_identity_id=ident.identity_id,
            external_entity_id="exec_run_999",
            description="Linked anomaly to agent execution run.",
            correlated_resource_ids=["kb_prod_01"],
        )

        # 11. Governance Evaluation
        gov_dec = self.governance_engine.evaluate_governance(
            tenant_id=tenant_id,
            subject_identity_id=ident.identity_id,
            target_action="READ",
            risk_score=risk_eval.composite_risk_score,
        )

        # 12. Privileged/Emergency Access Handling
        priv_req = self.privileged_access_manager.request_privileged_access(
            tenant_id=tenant_id,
            requester_identity_id=ident.identity_id,
            target_role_or_entitlement="ADMIN_ROLE",
            scope=PrivilegedAccessScope.PRODUCTION,
            justification="Emergency maintenance window",
        )

        # 13. Investigation
        inv = self.investigation_manager.open_investigation(
            tenant_id, "Agent Access Anomaly Investigation", ident.identity_id
        )
        self.investigation_manager.start_investigating(tenant_id, inv.investigation_id)
        self.investigation_manager.record_finding(tenant_id, inv.investigation_id, "Unused admin permission found")

        # 14. Remediation Planning
        rem_plan = self.remediation_manager.create_remediation_plan(
            tenant_id=tenant_id,
            target_identity_id=ident.identity_id,
            action=AccessRemediationAction.REVOKE_ENTITLEMENT,
            target_entitlement_id=ent2.entitlement_id,
        )

        # 15. Approval Evaluation & Delegation Generation
        del_req = self.remediation_manager.delegate_remediation(tenant_id, rem_plan.plan_id)

        # 16. External Verification
        verif = self.verification_manager.verify_remediation(
            tenant_id=tenant_id,
            remediation_plan_id=rem_plan.plan_id,
            checks=[
                VerificationCheck(
                    target_resource_id="rel_prod_01", expected_state="REVOKED", observed_state="REVOKED", passed=True
                )
            ],
        )

        # 17. Evidence Finalization
        evidence_bundle = self.evidence_manager.create_bundle(tenant_id, "Full Access Governance Evidence")
        self.evidence_manager.add_evidence(
            tenant_id,
            evidence_bundle.bundle_id,
            "AUTHORIZATION_DECISION",
            auth_dec.decision_id,
            {"outcome": auth_dec.outcome.value},
        )
        finalized_bundle = self.evidence_manager.finalize_bundle(tenant_id, evidence_bundle.bundle_id)

        # 18. Snapshot Generation
        concluded_inv = self.investigation_manager.conclude_investigation(tenant_id, inv.investigation_id)
        snap = self.snapshot_manager.capture_snapshot(
            tenant_id, concluded_inv.investigation_id, "ACCESS_INVESTIGATION", concluded_inv.model_dump(mode="json")
        )

        # 19. Trust Evaluation
        trust_asm = self.trust_engine.evaluate_identity_trust(tenant_id, ident.identity_id)

        # 20. Learning Recommendation
        learn_rec = self.learning_manager.record_access_pattern(
            tenant_id=tenant_id,
            identity_id=ident.identity_id,
            pattern_name="Off-Hours Admin Escalation",
            description="Identity escalates privileges off-hours.",
            recommended_action="CONSIDER_REVOKING_ROLE",
            reasoning="Reduce risk during unmonitored hours.",
        )

        # 21. Analytics Generation
        analytics_report = self.analytics_engine.generate_report(
            tenant_id=tenant_id, privileged_identities_count=1, toxic_combinations_count=len(tc_findings)
        )

        return {
            "status": "COMPLETED",
            "identity_id": ident.identity_id,
            "authorization_outcome": auth_dec.outcome.value,
            "governance_status": gov_dec.status.value,
            "risk_score": risk_eval.composite_risk_score,
            "evidence_hash": finalized_bundle.integrity.sha256_hash if finalized_bundle.integrity else None,
            "snapshot_id": snap.snapshot_id,
            "trust_score": trust_asm.score,
            "delegation_id": del_req.delegation_id,
        }
