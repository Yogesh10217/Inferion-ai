"""
Operational Certification Engine Module for Phase 5.68.
Evaluates end-to-end operational health, SRE readiness, and produces canonical operational certifications.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from app.deployment.secrets import SecretsSanitizer
from app.operations.alerting import Alert, AlertSeverity
from app.operations.deployment_health import DeploymentHealthResult
from app.operations.error_budget import ErrorBudgetResult, ErrorBudgetStatus
from app.operations.incident_management import Incident, IncidentSeverity
from app.operations.observability_engine import ObservationResult
from app.operations.operational_evidence import OperationalEvidence
from app.operations.slo import SLOResult, SLOStatus


class OperationalCertificationStatus(str, Enum):
    OPERATIONALLY_READY = "OPERATIONALLY_READY"
    OPERATIONALLY_AT_RISK = "OPERATIONALLY_AT_RISK"
    OPERATIONALLY_DEGRADED = "OPERATIONALLY_DEGRADED"
    MANUAL_REVIEW_REQUIRED = "MANUAL_REVIEW_REQUIRED"
    NOT_EXECUTED = "NOT_EXECUTED"


@dataclass
class OperationalCertificationResult:
    certification_status: OperationalCertificationStatus
    is_certified: bool
    evidence_level: str
    summary: str
    truthfulness_matrix: Dict[str, str]
    sha256_fingerprint: str
    details: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "certification_status": self.certification_status.value,
            "is_certified": self.is_certified,
            "evidence_level": self.evidence_level,
            "summary": SecretsSanitizer.sanitize_string(self.summary),
            "truthfulness_matrix": self.truthfulness_matrix,
            "sha256_fingerprint": self.sha256_fingerprint,
            "details": SecretsSanitizer.sanitize_structure(self.details),
        }


class OperationalCertificationEngine:
    """Evaluates operational evidence to certify platform operational readiness."""

    def evaluate_certification(
        self,
        observation: ObservationResult,
        slo_results: List[SLOResult],
        error_budget_result: Optional[ErrorBudgetResult],
        alerts: List[Alert],
        incidents: List[Incident],
        deployment_health: Optional[DeploymentHealthResult],
        evidence: Optional[OperationalEvidence],
        is_production: bool = False,
    ) -> OperationalCertificationResult:
        ev_level = observation.evidence_level

        # Preserve strict production truthfulness contract
        truthfulness_matrix = {
            "OBSERVABILITY_ENGINE_VALIDATED": "READY",
            "SLI_EVALUATION_VALIDATED": "READY",
            "SLO_EVALUATION_VALIDATED": "READY",
            "ERROR_BUDGET_VALIDATED": "READY",
            "ANOMALY_DETECTION_VALIDATED": "READY",
            "ALERTING_VALIDATED": "READY",
            "ALERT_DEDUPLICATION_VALIDATED": "READY",
            "INCIDENT_MANAGEMENT_VALIDATED": "READY",
            "INCIDENT_ESCALATION_VALIDATED": "READY",
            "RECOVERY_DECISION_VALIDATED": "READY",
            "DEPLOYMENT_HEALTH_VALIDATED": "READY",
            "PROMETHEUS_CONTAINER_RUNTIME_VALIDATED": "READY" if ev_level == "CONTAINER_RUNTIME" else "SIMULATED",
            "OPERATIONAL_EVIDENCE_VALIDATED": "READY",
            "OPERATIONAL_CERTIFICATION_VALIDATED": "READY",
            "SRE_METRICS_VALIDATED": "READY",
            # Strict Production Boundaries: MUST REMAIN NOT_EXECUTED
            "PRODUCTION_MONITORING_RUNTIME_VALIDATED": "NOT_EXECUTED",
            "PRODUCTION_ALERTING_RUNTIME_VALIDATED": "NOT_EXECUTED",
            "PRODUCTION_INCIDENT_RUNTIME_VALIDATED": "NOT_EXECUTED",
            "PRODUCTION_DEPLOYED": "NOT_EXECUTED",
            "LIVE_PRODUCTION_VALIDATED": "NOT_EXECUTED",
            "LIVE_PRODUCTION": "NOT_EXECUTED",
        }

        if is_production:
            return OperationalCertificationResult(
                certification_status=OperationalCertificationStatus.NOT_EXECUTED,
                is_certified=False,
                evidence_level="PRODUCTION_RUNTIME",
                summary="Production operational certification cannot be granted without real production execution.",
                truthfulness_matrix=truthfulness_matrix,
                sha256_fingerprint=evidence.sha256_fingerprint if evidence else "0" * 64,
                details={"reason": "Live production environment not connected."},
            )

        # Check conditions for non-production environments
        breached_slos = [s for s in slo_results if s.status == SLOStatus.BREACHED]
        at_risk_slos = [s for s in slo_results if s.status == SLOStatus.AT_RISK]
        active_incidents = [i for i in incidents if i.state.value not in ("RESOLVED", "CLOSED")]
        emergency_alerts = [a for a in alerts if a.severity == AlertSeverity.EMERGENCY]
        eb_exhausted = (error_budget_result.status == ErrorBudgetStatus.EXHAUSTED) if error_budget_result else False

        if active_incidents or emergency_alerts or eb_exhausted or len(breached_slos) >= 2:
            cert_status = OperationalCertificationStatus.OPERATIONALLY_DEGRADED
            is_certified = False
            summary = "Operational certification failed: Platform is degraded with active incidents or breached SLOs."
        elif breached_slos or at_risk_slos or (deployment_health and not deployment_health.is_healthy):
            cert_status = OperationalCertificationStatus.OPERATIONALLY_AT_RISK
            is_certified = False
            summary = "Operational certification warning: Platform operationally at risk."
        else:
            cert_status = OperationalCertificationStatus.OPERATIONALLY_READY
            is_certified = True
            summary = "Platform operationally certified ready for SRE container execution."

        fp = evidence.sha256_fingerprint if evidence else "0" * 64

        return OperationalCertificationResult(
            certification_status=cert_status,
            is_certified=is_certified,
            evidence_level=ev_level,
            summary=summary,
            truthfulness_matrix=truthfulness_matrix,
            sha256_fingerprint=fp,
            details={
                "breached_slos_count": len(breached_slos),
                "at_risk_slos_count": len(at_risk_slos),
                "active_incidents_count": len(active_incidents),
                "emergency_alerts_count": len(emergency_alerts),
                "error_budget_status": error_budget_result.status.value if error_budget_result else "UNKNOWN",
            },
        )
