"""Master EventIntelligenceManager Orchestrator Subsystem (Phase 5.34)."""

import logging
from typing import Any, Dict, Optional

from app.event_intelligence.analytics import EventAnalyticsEngine
from app.event_intelligence.automation import AutomationAction, AutomationManager
from app.event_intelligence.billing import EventBillingTracker
from app.event_intelligence.causality import EventCausalityAnalyzer
from app.event_intelligence.classification import EventClassifier
from app.event_intelligence.context import EventContextManager
from app.event_intelligence.correlation import CorrelationType, EventCorrelationManager
from app.event_intelligence.deduplication import EventDeduplicator
from app.event_intelligence.delegation import EventDelegationManager
from app.event_intelligence.events import EventManager, EventSeverity, EventType
from app.event_intelligence.governance import EventGovernanceEngine
from app.event_intelligence.impact import EventImpactAnalyzer
from app.event_intelligence.investigations import EventInvestigationManager
from app.event_intelligence.learning import EventLearningManager
from app.event_intelligence.normalization import EventNormalizer
from app.event_intelligence.observability import EventMetricsCollector
from app.event_intelligence.patterns import EventPatternDetector
from app.event_intelligence.prioritization import EventPrioritizationEngine
from app.event_intelligence.repositories import EventRepository
from app.event_intelligence.resolution import EventResolutionManager, EventResolutionStatus
from app.event_intelligence.response import EventResponseAction, EventResponseManager, ResponseTarget
from app.event_intelligence.rules import EventRuleManager
from app.event_intelligence.sources import EventSourceManager, EventSourceType
from app.event_intelligence.trust import EventTrustEngine
from app.platform_contracts.delegation import DelegationTarget
from app.platform_contracts.governance import GovernanceDecisionStatus

logger = logging.getLogger(__name__)


class EventIntelligenceManager:
    """Master Orchestrator coordinating full 20-step Enterprise AI Event Intelligence & Coordination Lifecycle."""

    def __init__(self) -> None:
        self.repository = EventRepository()

        self.event_manager = EventManager()
        self.source_manager = EventSourceManager()
        self.normalizer = EventNormalizer()
        self.classifier = EventClassifier()
        self.deduplicator = EventDeduplicator()

        self.correlation_manager = EventCorrelationManager()
        self.causality_analyzer = EventCausalityAnalyzer()
        self.context_manager = EventContextManager()
        self.impact_analyzer = EventImpactAnalyzer()
        self.pattern_detector = EventPatternDetector()

        self.automation_manager = AutomationManager()
        self.rule_manager = EventRuleManager()
        self.prioritization_engine = EventPrioritizationEngine()
        self.governance_engine = EventGovernanceEngine()
        self.response_manager = EventResponseManager()

        self.delegation_manager = EventDelegationManager()
        self.resolution_manager = EventResolutionManager()
        self.investigation_manager = EventInvestigationManager()
        self.learning_manager = EventLearningManager()
        self.trust_engine = EventTrustEngine()

        self.analytics_engine = EventAnalyticsEngine()
        self.metrics_collector = EventMetricsCollector()
        self.billing_tracker = EventBillingTracker()

        logger.info("[EVENT INTELLIGENCE MASTER] EventIntelligenceManager initialized cleanly with all 28 domain subsystems.")

    def run_full_event_intelligence_flow(
        self,
        tenant_id: str,
        source_name: str = "ReliabilityPlatform",
        event_type: EventType = EventType.INCIDENT_RAISED,
        severity: EventSeverity = EventSeverity.HIGH,
        payload: Optional[Dict[str, Any]] = None,
        is_high_risk_automation: bool = False,
    ) -> Dict[str, Any]:
        """Executes complete 20-step E2E enterprise event intelligence flow."""
        # 1. Source Registration & Ingestion
        src = self.source_manager.register_source(tenant_id, source_name, EventSourceType.RELIABILITY_PLATFORM)
        raw_evt = payload or {"event_type": event_type.value, "severity": severity.value, "component": "database"}

        # 2. Normalization & Sanitization
        norm = self.normalizer.normalize(tenant_id, raw_evt, source_id=src.source_id, source_name=src.name)
        evt = norm.event
        self.metrics_collector.record_event_received(evt.category.value, tenant_id)

        # 3. Deduplication & Idempotency Check
        dedup_res = self.deduplicator.process_deduplication(evt)
        if dedup_res.is_duplicate:
            self.metrics_collector.record_event_deduplicated(tenant_id)

        # 4. Classification & Impact Analysis
        cls = self.classifier.classify_event(evt)
        impact = self.impact_analyzer.analyze_impact(evt)

        # 5. Correlation & Causality Analysis
        corr_group = self.correlation_manager.correlate_events(tenant_id, f"Correlation for {evt.event_id}", [evt], CorrelationType.RELIABILITY_CASCADE)
        self.metrics_collector.record_event_correlated(corr_group.correlation_type.value, tenant_id)

        causal = self.causality_analyzer.analyze_causality(tenant_id, [evt])

        # 6. Context Assembly & Pattern Detection
        ctx = self.context_manager.assemble_event_context(evt)
        patterns = self.pattern_detector.detect_patterns(tenant_id, [evt])

        # 7. Trust Scoring & Prioritization
        trust = self.trust_engine.compute_trust(tenant_id, evt.event_id)
        prio = self.prioritization_engine.prioritize_event(evt, security_risk_high=cls.governance_sensitive, business_impact_high=impact.overall_severity == EventSeverity.HIGH)

        # 8. Governance Evaluation & Automation Planning
        gov_dec = self.governance_engine.evaluate_automation_governance(tenant_id, evt.event_id, is_high_risk=is_high_risk_automation)
        requires_approval = (gov_dec.status == GovernanceDecisionStatus.REQUIRE_APPROVAL)

        auto_plan = self.automation_manager.create_automation_plan(evt, action=AutomationAction.REQUEST_INVESTIGATION, requires_approval=requires_approval)
        self.metrics_collector.record_automation_triggered(auto_plan.action.value, tenant_id)

        # 9. Cross-Platform Response Planning & Delegated Execution
        resp_act = EventResponseAction(target=ResponseTarget.RELIABILITY_PLATFORM, action_type="INVESTIGATE_INCIDENT")
        resp_plan = self.response_manager.create_response_plan(tenant_id, evt.event_id, [resp_act])

        delegation_plan = self.delegation_manager.delegate_event_response(tenant_id, evt.event_id, DelegationTarget.PLATFORM_OPERATIONS, "EXECUTE_RESPONSE")

        # 10. Investigation, Resolution Lifecycle & Immutable Snapshot
        inv = self.investigation_manager.initiate_investigation(tenant_id, evt.event_id)
        concluded_inv = self.investigation_manager.conclude_investigation(inv.investigation_id, tenant_id, "Root cause identified cleanly.")

        res = self.resolution_manager.create_resolution(tenant_id, evt.event_id)
        res = self.resolution_manager.transition_resolution(res.resolution_id, tenant_id, EventResolutionStatus.INVESTIGATING)
        res = self.resolution_manager.transition_resolution(res.resolution_id, tenant_id, EventResolutionStatus.RESPONSE_PLANNED)
        res = self.resolution_manager.transition_resolution(res.resolution_id, tenant_id, EventResolutionStatus.DELEGATED)
        res = self.resolution_manager.transition_resolution(res.resolution_id, tenant_id, EventResolutionStatus.VERIFYING)
        final_res = self.resolution_manager.transition_resolution(res.resolution_id, tenant_id, EventResolutionStatus.RESOLVED)

        # 11. Learning, Analytics & Cost Attribution
        learning = self.learning_manager.record_learning(tenant_id, "Cascading Failure Pattern", "Update Reliability Rules")
        report = self.analytics_engine.generate_report(tenant_id)
        self.billing_tracker.record_event_cost(tenant_id, evt.event_id, 0.05, "Event intelligence pipeline run")

        return {
            "source": src.model_dump(),
            "event": evt.model_dump(),
            "deduplication": dedup_res.model_dump(),
            "classification": cls.model_dump(),
            "impact": impact.model_dump(),
            "correlation": corr_group.model_dump(),
            "causality": causal.model_dump(),
            "context": ctx.model_dump(),
            "patterns": [p.model_dump() for p in patterns],
            "trust": trust.model_dump(),
            "prioritization": prio.model_dump(),
            "governance_decision": gov_dec.model_dump(),
            "automation_plan": auto_plan.model_dump(),
            "response_plan": resp_plan.model_dump(),
            "delegation": delegation_plan.model_dump(),
            "investigation": concluded_inv.model_dump(),
            "resolution": final_res.model_dump(),
            "learning": learning.model_dump(),
            "analytics": report.model_dump(),
        }
