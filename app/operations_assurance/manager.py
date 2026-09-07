"""Master Orchestrator for Operations Assurance Platform."""

import logging
from typing import Dict, Any, List, Optional

from app.operations_assurance.services import ServiceIntelligenceManager, ServiceReference, ServiceType, ServiceStatus, ServiceTier, ServiceCriticality
from app.operations_assurance.service_health import ServiceHealthManager, ServiceHealthAssessment, ServiceHealthStatus
from app.operations_assurance.service_dependencies import ServiceDependencyManager, ServiceDependency, DependencyType, DependencyCriticality
from app.operations_assurance.dependency_graph import AnalyticalDependencyGraph
from app.operations_assurance.events import OperationalEventManager, OperationalEvent, OperationalEventType, OperationalSeverity
from app.operations_assurance.anomalies import OperationalAnomalyDetector, OperationalAnomaly, AnomalyCategory
from app.operations_assurance.reliability import OperationsReliabilityEngine, ReliabilityAssessment
from app.operations_assurance.availability import OperationsAvailabilityEngine, AvailabilityReport
from app.operations_assurance.performance import OperationsPerformanceEngine, PerformanceMetrics
from app.operations_assurance.capacity import OperationsCapacityEngine, CapacityAssessment, CapacityResourceType
from app.operations_assurance.forecasting import OperationsForecastingEngine, OperationalForecast, ForecastScenario
from app.operations_assurance.incidents import OperationalIncidentManager, OperationalIncident, OperationalIncidentState, OperationalIncidentSeverity
from app.operations_assurance.root_cause import OperationsRootCauseEngine, RootCauseAssessment, RootCauseCategory
from app.operations_assurance.blast_radius import OperationsBlastRadiusEngine, OperationalBlastRadiusAssessment
from app.operations_assurance.impact import OperationsImpactEngine, OperationalImpactScore
from app.operations_assurance.recommendations import OperationalRecommendationManager, OperationalRecommendation, OperationalRecommendationType
from app.operations_assurance.planning import OperationalPlanner, OperationalPlan, PlanningStrategy
from app.operations_assurance.runbooks import OperationalRunbookEngine, OperationalRunbook, RunbookCategory
from app.operations_assurance.governance import OperationsGovernanceEngine, OperationsGovernanceRequest, OperationsGovernanceResult
from app.operations_assurance.risk import OperationsRiskEngine, OperationalRiskAssessment
from app.operations_assurance.remediation import OperationsRemediationPlanner, RemediationPlan
from app.operations_assurance.delegation import OperationsDelegationManager, OperationalDelegationPlan, OperationalDelegationAction
from app.operations_assurance.verification import OperationsVerificationEngine, VerificationResult, VerificationType
from app.operations_assurance.evidence import OperationalEvidenceManager, OperationalEvidence
from app.operations_assurance.investigations import OperationalInvestigationManager, OperationalInvestigation
from app.operations_assurance.signals import OperationalSignalEngine, OperationalSignal, OperationalSignalType
from app.operations_assurance.correlation import OperationsCorrelationEngine, OperationalCorrelationResult
from app.operations_assurance.assurance import OperationsAssuranceEngine, OperationsAssuranceScore
from app.operations_assurance.trust import OperationsTrustEngine
from app.operations_assurance.snapshots import OperationalAssuranceSnapshotManager, OperationalAssuranceSnapshot
from app.operations_assurance.learning import OperationsLearningManager, OperationalLearningRecord
from app.operations_assurance.analytics import OperationsAnalyticsEngine, OperationsReport
from app.operations_assurance.observability import OperationsObservabilityEngine
from app.operations_assurance.billing import OperationsBillingTracker

logger = logging.getLogger(__name__)


class OperationsAssuranceManager:
    """Master Orchestrator for Enterprise AI Operations Intelligence & Autonomous Service Assurance."""

    def __init__(self) -> None:
        self.service_manager = ServiceIntelligenceManager()
        self.health_manager = ServiceHealthManager()
        self.dependency_manager = ServiceDependencyManager()
        self.dependency_graph = AnalyticalDependencyGraph()
        self.event_manager = OperationalEventManager()
        self.anomaly_detector = OperationalAnomalyDetector()
        self.reliability_engine = OperationsReliabilityEngine()
        self.availability_engine = OperationsAvailabilityEngine()
        self.performance_engine = OperationsPerformanceEngine()
        self.capacity_engine = OperationsCapacityEngine()
        self.forecasting_engine = OperationsForecastingEngine()
        self.incident_manager = OperationalIncidentManager()
        self.root_cause_engine = OperationsRootCauseEngine()
        self.blast_radius_engine = OperationsBlastRadiusEngine()
        self.impact_engine = OperationsImpactEngine()
        self.recommendation_manager = OperationalRecommendationManager()
        self.planner = OperationalPlanner()
        self.runbook_engine = OperationalRunbookEngine()
        self.governance_engine = OperationsGovernanceEngine()
        self.risk_engine = OperationsRiskEngine()
        self.remediation_planner = OperationsRemediationPlanner()
        self.delegation_manager = OperationsDelegationManager()
        self.verification_engine = OperationsVerificationEngine()
        self.evidence_manager = OperationalEvidenceManager()
        self.investigation_manager = OperationalInvestigationManager()
        self.signal_engine = OperationalSignalEngine()
        self.correlation_engine = OperationsCorrelationEngine()
        self.assurance_engine = OperationsAssuranceEngine()
        self.trust_engine = OperationsTrustEngine()
        self.snapshot_manager = OperationalAssuranceSnapshotManager()
        self.learning_manager = OperationsLearningManager()
        self.analytics_engine = OperationsAnalyticsEngine()
        self.observability_engine = OperationsObservabilityEngine()
        self.billing_tracker = OperationsBillingTracker()

    def register_service(
        self,
        tenant_id: str,
        name: str,
        service_type: ServiceType,
        tier: ServiceTier = ServiceTier.TIER_1,
        criticality: ServiceCriticality = ServiceCriticality.CRITICAL,
    ) -> ServiceReference:
        service = self.service_manager.register_service(
            tenant_id=tenant_id,
            name=name,
            service_type=service_type,
            tier=tier,
            criticality=criticality,
        )
        self.health_manager.evaluate_health(tenant_id, service.service_id)
        self.observability_engine.record_service_count(tenant_id, len(self.service_manager.list_services(tenant_id)))
        self.billing_tracker.record_cost(tenant_id, service.service_id, "REGISTER_SERVICE")
        return service

    def evaluate_assurance(self, tenant_id: str, service_id: str) -> OperationsAssuranceScore:
        service = self.service_manager.get_service(tenant_id, service_id)
        health = self.health_manager.get_health(tenant_id, service_id)
        reliability = self.reliability_engine.assess_reliability(tenant_id, service_id)

        score = self.assurance_engine.compute_assurance_score(
            tenant_id=tenant_id,
            service_id=service_id,
            health_score=1.0 if health.status == ServiceHealthStatus.EXCELLENT else 0.8,
            reliability_score=reliability.reliability_score,
        )
        self.observability_engine.record_assurance_score(tenant_id, service_id, score.overall_score)
        return score
