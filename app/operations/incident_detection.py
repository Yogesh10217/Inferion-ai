"""
Incident Detection Engine Module for Phase 5.68.
Correlates deduplicated alerts, SLO breaches, anomalies, and health failures to trigger incidents or operational events.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from app.deployment.secrets import SecretsSanitizer
from app.operations.alerting import Alert, AlertSeverity
from app.operations.incident_management import Incident, IncidentManager, IncidentSeverity


@dataclass
class DetectionResult:
    decision: str  # "INCIDENT" or "OPERATIONAL_EVENT"
    incident: Optional[Incident]
    severity: Optional[IncidentSeverity]
    summary: str
    details: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "decision": self.decision,
            "incident": self.incident.to_dict() if self.incident else None,
            "severity": self.severity.value if self.severity else None,
            "summary": SecretsSanitizer.sanitize_string(self.summary),
            "details": SecretsSanitizer.sanitize_structure(self.details),
        }


class IncidentDetectionEngine:
    """Evaluates telemetry signals to classify incidents versus benign operational events."""

    def __init__(self, incident_manager: Optional[IncidentManager] = None) -> None:
        self.incident_manager = incident_manager or IncidentManager()

    def evaluate_signals(
        self,
        alerts: List[Alert],
        deployment_identity: str = "dep-568-prod-001",
    ) -> DetectionResult:
        if not alerts:
            return DetectionResult(
                decision="OPERATIONAL_EVENT",
                incident=None,
                severity=None,
                summary="No active alerts. System operationally healthy.",
                details={"active_alerts_count": 0},
            )

        has_emergency = any(a.severity == AlertSeverity.EMERGENCY for a in alerts)
        has_critical = any(a.severity == AlertSeverity.CRITICAL for a in alerts)
        has_warning = any(a.severity == AlertSeverity.WARNING for a in alerts)

        if has_emergency:
            sev = IncidentSeverity.P1
            summary = "P1 Critical Platform Outage: Emergency alerts triggered"
        elif has_critical:
            sev = IncidentSeverity.P2
            summary = "P2 Major Service Degradation: Critical alerts triggered"
        elif has_warning and len(alerts) >= 3:
            sev = IncidentSeverity.P3
            summary = "P3 Partial Degradation: Multiple warning alerts triggered"
        elif has_warning:
            sev = IncidentSeverity.P4
            summary = "P4 Minor Operational Issue: Single warning alert triggered"
        else:
            return DetectionResult(
                decision="OPERATIONAL_EVENT",
                incident=None,
                severity=None,
                summary="Informational operational events only.",
                details={"alerts": [a.to_dict() for a in alerts]},
            )

        inc = self.incident_manager.create_incident(
            title=summary,
            severity=sev,
            deployment_identity=deployment_identity,
            summary=summary,
            evidence={"alerts_count": len(alerts), "alerts": [a.to_dict() for a in alerts]},
        )

        return DetectionResult(
            decision="INCIDENT",
            incident=inc,
            severity=sev,
            summary=summary,
            details={"alerts_count": len(alerts), "incident_id": inc.incident_id},
        )
