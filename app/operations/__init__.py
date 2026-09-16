"""
Operations, Observability, SRE, and Incident Management package for Enterprise AI Platform.
Phase 5.68 canonical operations module.
"""

from app.operations.alert_deduplication import AlertDeduplicationEngine, AlertFingerprint
from app.operations.alerting import Alert, AlertEngine, AlertSeverity, AlertStatus
from app.operations.anomaly_detection import Anomaly, AnomalySeverity, AnomalyType, RuleBasedAnomalyDetector
from app.operations.deployment_health import DeploymentHealthCorrelator, DeploymentHealthResult
from app.operations.error_budget import ErrorBudget, ErrorBudgetEvaluator, ErrorBudgetResult, ErrorBudgetStatus
from app.operations.incident_detection import IncidentDetectionEngine
from app.operations.incident_escalation import EscalationResult, IncidentEscalationEngine, NotificationReadiness
from app.operations.incident_management import Incident, IncidentManager, IncidentSeverity, IncidentStatus
from app.operations.incident_state_machine import IllegalStateTransitionError, IncidentState, IncidentStateMachine
from app.operations.observability_engine import (
    ObservabilityEngine,
    ObservationResult,
    ObservationStatus,
    RuntimeObservation,
)
from app.operations.operational_certification import (
    OperationalCertificationEngine,
    OperationalCertificationResult,
    OperationalCertificationStatus,
)
from app.operations.operational_dashboard import OperationalDashboardSnapshot
from app.operations.operational_evidence import OperationalEvidence, OperationalEvidenceCollector
from app.operations.operations_orchestrator import OperationsOrchestrator
from app.operations.post_incident import PostIncidentReport, PostIncidentReportGenerator
from app.operations.prometheus_observability import PrometheusObservabilityAdapter, PrometheusRuntimeStatus
from app.operations.recovery_decision import RecoveryDecision, RecoveryDecisionEngine, RecoveryRecommendation
from app.operations.sli import ServiceLevelIndicator, SLIEvaluator, SLIResult, SLIType
from app.operations.slo import ServiceLevelObjective, SLOEvaluator, SLOResult, SLOStatus
from app.operations.sre_metrics import SREMetricsCalculator, SREMetricsResult

__all__ = [
    "ObservabilityEngine",
    "RuntimeObservation",
    "ObservationStatus",
    "ObservationResult",
    "ServiceLevelIndicator",
    "SLIEvaluator",
    "SLIResult",
    "SLIType",
    "ServiceLevelObjective",
    "SLOEvaluator",
    "SLOResult",
    "SLOStatus",
    "ErrorBudget",
    "ErrorBudgetEvaluator",
    "ErrorBudgetResult",
    "ErrorBudgetStatus",
    "RuleBasedAnomalyDetector",
    "Anomaly",
    "AnomalyType",
    "AnomalySeverity",
    "AlertEngine",
    "Alert",
    "AlertSeverity",
    "AlertStatus",
    "AlertDeduplicationEngine",
    "AlertFingerprint",
    "IncidentManager",
    "Incident",
    "IncidentSeverity",
    "IncidentStatus",
    "IncidentStateMachine",
    "IncidentState",
    "IllegalStateTransitionError",
    "IncidentDetectionEngine",
    "IncidentEscalationEngine",
    "EscalationResult",
    "NotificationReadiness",
    "RecoveryDecisionEngine",
    "RecoveryDecision",
    "RecoveryRecommendation",
    "DeploymentHealthCorrelator",
    "DeploymentHealthResult",
    "PrometheusObservabilityAdapter",
    "PrometheusRuntimeStatus",
    "OperationalDashboardSnapshot",
    "OperationalEvidenceCollector",
    "OperationalEvidence",
    "OperationalCertificationEngine",
    "OperationalCertificationResult",
    "OperationalCertificationStatus",
    "OperationsOrchestrator",
    "PostIncidentReportGenerator",
    "PostIncidentReport",
    "SREMetricsCalculator",
    "SREMetricsResult",
]
