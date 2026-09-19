"""Master Coordinator for Enterprise AI Observability, SRE & Autonomous Operations Platform."""

import logging
from typing import Any, Dict

from app.operations.alerting import AlertManager
from app.operations.analytics import OperationsAnalyticsEngine
from app.operations.change_intelligence import ChangeCorrelationEngine
from app.operations.incidents import IncidentManager
from app.operations.observability import OperationsMetricsCollector
from app.operations.postmortem import PostmortemManager
from app.operations.prediction import FailurePredictionEngine
from app.operations.remediation import AutonomousRemediationEngine
from app.operations.root_cause import RootCauseAnalysisEngine
from app.operations.runbooks import RunbookManager
from app.operations.slo import SLOManager
from app.operations.storage import TelemetryRetentionManager
from app.operations.telemetry import TelemetryManager
from app.operations.topology import TopologyManager

logger = logging.getLogger(__name__)


class OperationsManager:
    """Master Coordinator orchestrating Telemetry, Topology, SLOs, Alerting, Incidents, RCA, Change Intelligence, Failure Prediction, Runbooks, Remediation, Postmortems, Operations Analytics, and Retention."""

    def __init__(self) -> None:
        self.telemetry_manager = TelemetryManager()
        self.topology_manager = TopologyManager()
        self.slo_manager = SLOManager()
        self.alert_manager = AlertManager()
        self.incident_manager = IncidentManager()
        self.rca_engine = RootCauseAnalysisEngine(topology_manager=self.topology_manager)
        self.change_engine = ChangeCorrelationEngine()
        self.prediction_engine = FailurePredictionEngine()
        self.runbook_manager = RunbookManager()
        self.remediation_engine = AutonomousRemediationEngine(runbook_manager=self.runbook_manager)
        self.postmortem_manager = PostmortemManager()
        self.analytics_engine = OperationsAnalyticsEngine(incident_manager=self.incident_manager)
        self.retention_manager = TelemetryRetentionManager()
        self.metrics_collector = OperationsMetricsCollector()

        logger.info(
            "[OPERATIONS MANAGER] Master OperationsManager initialized with all 15 operational domain subsystems"
        )

    def get_summary(self) -> Dict[str, Any]:
        return {
            "registered_nodes": len(self.topology_manager.list_nodes()),
            "active_slos": len(self.slo_manager.list_slos()),
            "active_alerts": len(self.alert_manager.list_alerts()),
            "open_incidents": len(self.incident_manager.list_incidents()),
            "registered_runbooks": len(self.runbook_manager.list_runbooks()),
            "metrics": self.metrics_collector.get_summary(),
        }
