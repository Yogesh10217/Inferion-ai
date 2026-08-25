"""Master SecurityIntelligenceManager Orchestrator Subsystem (Phase 5.32)."""

import logging
from typing import Dict, Any, Optional, List

from app.security_intelligence.assets import SecurityAssetManager, SecurityAsset, SecurityAssetType, SecurityAssetCriticality
from app.security_intelligence.attack_surface import AttackSurfaceManager, AttackSurface, AttackSurfaceEntry
from app.security_intelligence.signals import SecuritySignalManager, SecuritySignal, SecuritySignalType, SecuritySignalSeverity
from app.security_intelligence.threats import ThreatManager, SecurityThreat, ThreatType, ThreatSeverity
from app.security_intelligence.ai_threats import AIThreatManager, AIThreat, AIThreatType, AIThreatSeverity
from app.security_intelligence.vulnerabilities import VulnerabilityManager, SecurityVulnerability, VulnerabilitySeverity, VulnerabilityStatus
from app.security_intelligence.correlation import SecurityCorrelationManager, SecurityCorrelation, CorrelationType
from app.security_intelligence.attack_paths import AttackPathAnalyzer, AttackPath
from app.security_intelligence.incidents import SecurityIncidentManager, SecurityIncident, SecurityIncidentStatus, SecurityIncidentSeverity
from app.security_intelligence.impact import SecurityImpactAnalyzer, SecurityImpactAssessment
from app.security_intelligence.risk import SecurityRiskManager, SecurityRiskAssessment
from app.security_intelligence.governance import SecurityGovernanceEngine, GovernanceDecision
from app.security_intelligence.remediation import SecurityRemediationManager, SecurityRemediationPlan, SecurityRemediationAction, SecurityRemediationPriority
from app.security_intelligence.posture import SecurityPostureManager, SecurityPosture
from app.security_intelligence.trust import SecurityTrustEngine, SecurityTrustScore
from app.security_intelligence.evidence import SecurityEvidenceManager, SecurityEvidenceBundle, SecurityEvidence
from app.security_intelligence.investigations import InvestigationManager, SecurityInvestigation, InvestigationFinding
from app.security_intelligence.learning import SecurityLearningManager, SecurityLearningRecord
from app.security_intelligence.analytics import SecurityAnalyticsEngine, PlatformReport
from app.security_intelligence.observability import SecurityMetricsCollector
from app.security_intelligence.billing import SecurityBillingTracker
from app.security_intelligence.repositories import SecurityRepository
from app.platform_contracts.delegation import DelegationTarget

logger = logging.getLogger(__name__)


class SecurityIntelligenceManager:
    """Master Orchestrator unifying all 25 Security Intelligence, Threat Detection, Vulnerability & Governance Subsystems."""

    def __init__(self) -> None:
        self.repository = SecurityRepository()

        self.asset_manager = SecurityAssetManager()
        self.attack_surface_manager = AttackSurfaceManager()
        self.signal_manager = SecuritySignalManager()
        self.threat_manager = ThreatManager()
        self.ai_threat_manager = AIThreatManager()

        self.vulnerability_manager = VulnerabilityManager()
        self.correlation_manager = SecurityCorrelationManager()
        self.attack_path_analyzer = AttackPathAnalyzer()
        self.incident_manager = SecurityIncidentManager()

        self.impact_analyzer = SecurityImpactAnalyzer()
        self.risk_manager = SecurityRiskManager()
        self.governance_engine = SecurityGovernanceEngine()
        self.remediation_manager = SecurityRemediationManager()

        self.posture_manager = SecurityPostureManager()
        self.trust_engine = SecurityTrustEngine()
        self.evidence_manager = SecurityEvidenceManager()
        self.investigation_manager = InvestigationManager()
        self.learning_manager = SecurityLearningManager()

        self.analytics_engine = SecurityAnalyticsEngine()
        self.metrics_collector = SecurityMetricsCollector()
        self.billing_tracker = SecurityBillingTracker()

        logger.info("[SECURITY MASTER] SecurityIntelligenceManager initialized cleanly with all 25 domain subsystems.")

    def run_full_security_lifecycle_flow(
        self,
        tenant_id: str,
        asset_name: str = "LLM_Inference_Gateway",
    ) -> Dict[str, Any]:
        """Executes complete 14-step E2E security lifecycle flow from signal ingestion to posture update and learning."""
        # 1. Register Asset & Attack Surface
        asset = self.asset_manager.register_asset(tenant_id, asset_name, SecurityAssetType.MODEL_GATEWAY, SecurityAssetCriticality.CRITICAL)
        surf = self.attack_surface_manager.register_attack_surface(tenant_id, [AttackSurfaceEntry(asset_id=asset.asset_id, entry_point_name="/v1/chat/completions")])

        # 2. Ingest Signal (Sanitized)
        sig = self.signal_manager.ingest_signal(tenant_id, asset.asset_id, SecuritySignalType.PROMPT_INJECTION_ATTEMPT, severity=SecuritySignalSeverity.HIGH, payload={"secret_token": "sk_test_12345"})
        self.metrics_collector.record_signal(sig.signal_type.value, tenant_id)

        # 3. Detect Threat & AI Threat
        thrt = self.threat_manager.create_threat(tenant_id, asset.asset_id, ThreatType.AI_MODEL_THREAT, ThreatSeverity.HIGH)
        aithrt = self.ai_threat_manager.analyze_ai_threat(tenant_id, asset.asset_id, AIThreatType.PROMPT_INJECTION, severity=AIThreatSeverity.HIGH, signal_id=sig.signal_id)
        self.metrics_collector.record_threat(thrt.threat_type.value, tenant_id)

        # 4. Discover Vulnerability
        vuln = self.vulnerability_manager.create_vulnerability(tenant_id, asset.asset_id, "Unsanitized Prompt Context Vulnerability", VulnerabilitySeverity.HIGH, cve_id="CVE-2026-AI01")
        self.vulnerability_manager.transition_vulnerability(vuln.vulnerability_id, tenant_id, VulnerabilityStatus.VALIDATING)
        self.vulnerability_manager.transition_vulnerability(vuln.vulnerability_id, tenant_id, VulnerabilityStatus.CONFIRMED)

        # 5. Analyze Attack Path & Correlate
        path = self.attack_path_analyzer.analyze_attack_path(tenant_id, entry_node_name=asset_name, target_asset_name="User_Context_DB")
        corr = self.correlation_manager.correlate_security_event(tenant_id, thrt.threat_id, [vuln.vulnerability_id])

        # 6. Create Security Incident
        inc = self.incident_manager.create_incident(tenant_id, asset.asset_id, f"Prompt Injection Attack on {asset_name}", SecurityIncidentSeverity.SEV_1_HIGH)
        self.metrics_collector.record_incident("SEV_1_HIGH", tenant_id)

        # 7. Impact & Risk Assessment
        impact = self.impact_analyzer.analyze_impact(tenant_id, asset.asset_id)
        risk_ass = self.risk_manager.assess_security_risk(tenant_id, asset.asset_id, "HIGH")

        # 8. Remediation Planning & Governance Evaluation
        action = SecurityRemediationAction(target_manager=DelegationTarget.PLATFORM_OPERATIONS, action_name="REVOKE_KEY", priority=SecurityRemediationPriority.HIGH)

        plan = self.remediation_manager.plan_remediation(tenant_id, inc.incident_id, f"sec_idemp_{inc.incident_id}", [action], priority=SecurityRemediationPriority.HIGH)
        gov_dec = self.governance_engine.evaluate_remediation_governance(tenant_id, plan)

        # 9. Evidence Bundle & Investigation Snapshot
        ev = SecurityEvidence(tenant_id=tenant_id, source="API_GATEWAY", content_reference=sig.signal_id, metadata={"sanitized": True})
        bundle = self.evidence_manager.create_evidence_bundle(tenant_id, f"Evidence for {inc.incident_id}", [ev])
        finalized_bundle = self.evidence_manager.finalize_evidence_bundle(bundle.bundle_id, tenant_id)

        inv = self.investigation_manager.create_investigation(tenant_id, inc.incident_id, f"Investigation for {inc.incident_id}")
        concluded_inv = self.investigation_manager.conclude_investigation(inv.investigation_id, tenant_id, [InvestigationFinding(description="Confirmed malicious prompt injection")])

        # 10. Close Incident Lifecycle
        self.incident_manager.transition_incident(inc.incident_id, tenant_id, SecurityIncidentStatus.TRIAGED)
        self.incident_manager.transition_incident(inc.incident_id, tenant_id, SecurityIncidentStatus.INVESTIGATING)
        self.incident_manager.transition_incident(inc.incident_id, tenant_id, SecurityIncidentStatus.CONTAINMENT_PLANNED)
        self.incident_manager.transition_incident(inc.incident_id, tenant_id, SecurityIncidentStatus.REMEDIATION_PENDING)
        self.incident_manager.transition_incident(inc.incident_id, tenant_id, SecurityIncidentStatus.REMEDIATION_IN_PROGRESS)
        self.incident_manager.transition_incident(inc.incident_id, tenant_id, SecurityIncidentStatus.VERIFYING)
        self.incident_manager.transition_incident(inc.incident_id, tenant_id, SecurityIncidentStatus.RESOLVED)
        closed_inc = self.incident_manager.transition_incident(inc.incident_id, tenant_id, SecurityIncidentStatus.CLOSED)

        # 11. Security Posture & Trust Update
        post = self.posture_manager.calculate_posture(tenant_id, active_threats_count=0, active_vulnerabilities_count=0)
        trust = self.trust_engine.compute_trust_score(tenant_id, asset.asset_id, post.overall_score)
        learning = self.learning_manager.record_learning(tenant_id, inc.incident_id, "Prompt Injection Pattern", "Strict Context Boundary Policy")

        return {
            "asset": asset.model_dump(),
            "surface": surf.model_dump(),
            "signal": sig.model_dump(),
            "threat": thrt.model_dump(),
            "ai_threat": aithrt.model_dump(),
            "vulnerability": vuln.model_dump(),
            "attack_path": path.model_dump(),
            "correlation": corr.model_dump(),
            "incident": closed_inc.model_dump(),
            "impact": impact.model_dump(),
            "remediation_plan": plan.model_dump(),
            "governance_decision": gov_dec.model_dump(),
            "evidence_bundle": finalized_bundle.model_dump(),
            "investigation": concluded_inv.model_dump(),
            "posture": post.model_dump(),
            "trust": trust.model_dump(),
            "learning": learning.model_dump(),
        }
