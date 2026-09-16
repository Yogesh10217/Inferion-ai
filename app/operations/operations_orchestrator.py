"""
Operations Orchestrator Module for Phase 5.68.
Canonical end-to-end orchestration entry point executing the operational telemetry pipeline.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from app.operations.alert_deduplication import AlertDeduplicationEngine
from app.operations.alerting import Alert, AlertEngine
from app.operations.anomaly_detection import Anomaly, RuleBasedAnomalyDetector
from app.operations.deployment_health import DeploymentHealthCorrelator, DeploymentHealthResult
from app.operations.error_budget import ErrorBudgetEvaluator, ErrorBudgetResult
from app.operations.incident_detection import DetectionResult, IncidentDetectionEngine
from app.operations.incident_escalation import EscalationResult, IncidentEscalationEngine
from app.operations.incident_management import IncidentManager
from app.operations.observability_engine import ObservabilityEngine, ObservationResult
from app.operations.operational_certification import (
    OperationalCertificationEngine,
    OperationalCertificationResult,
)
from app.operations.operational_dashboard import OperationalDashboardSnapshot
from app.operations.operational_evidence import OperationalEvidence, OperationalEvidenceCollector
from app.operations.recovery_decision import RecoveryDecision, RecoveryDecisionEngine
from app.operations.sli import SLIEvaluator, SLIResult
from app.operations.slo import SLOEvaluator, SLOResult
from app.operations.sre_metrics import SREMetricsCalculator, SREMetricsResult


@dataclass
class OperationalPipelineResult:
    observation: ObservationResult
    sli_results: List[SLIResult]
    slo_results: List[SLOResult]
    error_budget: ErrorBudgetResult
    anomalies: List[Anomaly]
    raw_alerts: List[Alert]
    deduplicated_alerts: List[Alert]
    incident_detection: DetectionResult
    escalation_results: List[EscalationResult]
    recovery_decision: RecoveryDecision
    deployment_health: DeploymentHealthResult
    evidence: OperationalEvidence
    certification: OperationalCertificationResult
    dashboard_snapshot: OperationalDashboardSnapshot
    sre_metrics: SREMetricsResult

    def to_dict(self) -> Dict[str, Any]:
        return {
            "observation": self.observation.to_dict(),
            "sli_results": [s.to_dict() for s in self.sli_results],
            "slo_results": [s.to_dict() for s in self.slo_results],
            "error_budget": self.error_budget.to_dict(),
            "anomalies": [a.to_dict() for a in self.anomalies],
            "raw_alerts": [a.to_dict() for a in self.raw_alerts],
            "deduplicated_alerts": [a.to_dict() for a in self.deduplicated_alerts],
            "incident_detection": self.incident_detection.to_dict(),
            "escalation_results": [e.to_dict() for e in self.escalation_results],
            "recovery_decision": self.recovery_decision.to_dict(),
            "deployment_health": self.deployment_health.to_dict(),
            "evidence": self.evidence.to_dict(),
            "certification": self.certification.to_dict(),
            "dashboard_snapshot": self.dashboard_snapshot.to_dict(),
            "sre_metrics": self.sre_metrics.to_dict(),
        }


class OperationsOrchestrator:
    """Canonical Phase 5.68 Operations & SRE Pipeline Orchestrator."""

    def __init__(self) -> None:
        self.observability_engine = ObservabilityEngine()
        self.sli_evaluator = SLIEvaluator()
        self.slo_evaluator = SLOEvaluator()
        self.error_budget_evaluator = ErrorBudgetEvaluator()
        self.anomaly_detector = RuleBasedAnomalyDetector()
        self.alert_engine = AlertEngine()
        self.alert_deduplication_engine = AlertDeduplicationEngine()
        self.incident_manager = IncidentManager()
        self.incident_detection_engine = IncidentDetectionEngine(self.incident_manager)
        self.incident_escalation_engine = IncidentEscalationEngine()
        self.recovery_decision_engine = RecoveryDecisionEngine()
        self.deployment_health_correlator = DeploymentHealthCorrelator()
        self.evidence_collector = OperationalEvidenceCollector()
        self.certification_engine = OperationalCertificationEngine()
        self.sre_metrics_calculator = SREMetricsCalculator()

    def run_pipeline(
        self,
        app_data: Optional[Dict[str, Any]] = None,
        health_data: Optional[Dict[str, Any]] = None,
        dependency_data: Optional[Dict[str, Any]] = None,
        deployment_identity: str = "dep-568-prod-001",
        artifact_digest: str = "sha256:568c001a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e",
        release_candidate_id: str = "rc-5.68.0",
        traffic_percentage: float = 100.0,
        evidence_level: str = "CONTAINER_RUNTIME",
        is_production: bool = False,
    ) -> OperationalPipelineResult:
        # 1. Runtime Observation
        observation = self.observability_engine.collect_observations(
            app_data=app_data,
            health_data=health_data,
            dependency_data=dependency_data,
            evidence_level=evidence_level,
        )

        # 2. SLI Evaluation
        sli_results = self.sli_evaluator.evaluate(observation)

        # 3. SLO Evaluation
        slo_results = self.slo_evaluator.evaluate(sli_results)

        # 4. Error Budget Tracking
        error_budget = self.error_budget_evaluator.evaluate(slo_results, evidence_level=evidence_level)

        # 5. Anomaly Detection
        anomalies = self.anomaly_detector.detect_anomalies(observation)

        # 6. Alert Generation
        raw_alerts = self.alert_engine.generate_alerts(
            slo_results=slo_results,
            error_budget_result=error_budget,
            anomalies=anomalies,
            deployment_identity=deployment_identity,
        )

        # 7. Alert Deduplication
        dedup_alerts = self.alert_deduplication_engine.deduplicate(raw_alerts)

        # 8. Incident Detection
        inc_detection = self.incident_detection_engine.evaluate_signals(
            alerts=dedup_alerts,
            deployment_identity=deployment_identity,
        )

        # 9. Incident Escalation
        escalation_results = []
        if inc_detection.incident:
            esc_res = self.incident_escalation_engine.evaluate_escalation(
                incident=inc_detection.incident,
                unresolved_minutes=0,
                repeat_occurrence_count=1,
            )
            escalation_results.append(esc_res)

        # 10. Recovery Recommendation
        recovery_decision = self.recovery_decision_engine.evaluate_recovery(
            incident=inc_detection.incident,
            slo_results=slo_results,
            error_budget_result=error_budget,
            alerts=dedup_alerts,
            evidence_level=evidence_level,
        )

        # 11. Deployment Health Correlation
        active_incidents = list(self.incident_manager.active_incidents.values())
        dep_health = self.deployment_health_correlator.correlate(
            deployment_identity=deployment_identity,
            artifact_digest=artifact_digest,
            release_candidate_id=release_candidate_id,
            traffic_percentage=traffic_percentage,
            observation=observation,
            slo_results=slo_results,
            error_budget_result=error_budget,
            incidents=active_incidents,
        )

        # 12. Operational Evidence Fingerprinting
        raw_evidence_payload = {
            "deployment_identity": deployment_identity,
            "artifact_digest": artifact_digest,
            "observation": observation.to_dict(),
            "recovery_recommendation": recovery_decision.recommendation.value,
            "deployment_health_score": dep_health.health_score,
        }
        evidence = self.evidence_collector.create_evidence(
            raw_payload=raw_evidence_payload,
            evidence_level=evidence_level,
            evidence_id=f"ev-{deployment_identity}",
        )

        # 13. Operational Certification
        certification = self.certification_engine.evaluate_certification(
            observation=observation,
            slo_results=slo_results,
            error_budget_result=error_budget,
            alerts=dedup_alerts,
            incidents=active_incidents,
            deployment_health=dep_health,
            evidence=evidence,
            is_production=is_production,
        )

        # 14. Dashboard Snapshot
        dashboard = OperationalDashboardSnapshot(
            timestamp=observation.timestamp,
            platform_status=observation.status.value,
            availability=float(observation.application_metrics.get("availability", 1.0)),
            error_rate=float(observation.application_metrics.get("error_rate", 0.0)),
            latency_p50=float(observation.application_metrics.get("latency_p50", 0.0)),
            latency_p95=float(observation.application_metrics.get("latency_p95", 0.0)),
            latency_p99=float(observation.application_metrics.get("latency_p99", 0.0)),
            slo_status_counts=dep_health.slo_status_summary,
            error_budget_status=error_budget.status.value,
            active_alerts_count=len(dedup_alerts),
            active_incidents_count=len(active_incidents),
            deployment_health_score=dep_health.health_score,
            dependency_status={k: v.get("status", "HEALTHY") if isinstance(v, dict) else "HEALTHY" for k, v in observation.dependency_metrics.items()},
            certification_status=certification.certification_status.value,
            evidence_level=evidence_level,
            details={"certification_summary": certification.summary},
        )

        # 15. SRE Metrics
        all_incidents = list(self.incident_manager.active_incidents.values()) + list(self.incident_manager.closed_incidents.values())
        sre_metrics = self.sre_metrics_calculator.calculate_metrics(all_incidents)

        return OperationalPipelineResult(
            observation=observation,
            sli_results=sli_results,
            slo_results=slo_results,
            error_budget=error_budget,
            anomalies=anomalies,
            raw_alerts=raw_alerts,
            deduplicated_alerts=dedup_alerts,
            incident_detection=inc_detection,
            escalation_results=escalation_results,
            recovery_decision=recovery_decision,
            deployment_health=dep_health,
            evidence=evidence,
            certification=certification,
            dashboard_snapshot=dashboard,
            sre_metrics=sre_metrics,
        )
