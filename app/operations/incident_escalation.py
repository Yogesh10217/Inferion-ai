"""
Incident Escalation Engine Module for Phase 5.68.
Handles incident escalation policies (P4 -> P3 -> P2 -> P1) and notification readiness evaluation.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional

from app.deployment.secrets import SecretsSanitizer
from app.operations.incident_management import Incident, IncidentSeverity


class NotificationReadiness(str, Enum):
    NOTIFICATION_READY = "NOTIFICATION_READY"
    NOTIFICATION_SIMULATED = "NOTIFICATION_SIMULATED"
    NOTIFICATION_NOT_CONFIGURED = "NOTIFICATION_NOT_CONFIGURED"
    NOT_EXECUTED = "NOT_EXECUTED"


@dataclass
class EscalationResult:
    incident_id: str
    previous_severity: IncidentSeverity
    current_severity: IncidentSeverity
    is_escalated: bool
    notification_status: NotificationReadiness
    summary: str
    details: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "incident_id": self.incident_id,
            "previous_severity": self.previous_severity.value,
            "current_severity": self.current_severity.value,
            "is_escalated": self.is_escalated,
            "notification_status": self.notification_status.value,
            "summary": SecretsSanitizer.sanitize_string(self.summary),
            "details": SecretsSanitizer.sanitize_structure(self.details),
        }


class IncidentEscalationEngine:
    """Evaluates escalation thresholds and manages non-destructive notification status."""

    ESCALATION_LADDER = {
        IncidentSeverity.P4: IncidentSeverity.P3,
        IncidentSeverity.P3: IncidentSeverity.P2,
        IncidentSeverity.P2: IncidentSeverity.P1,
        IncidentSeverity.P1: IncidentSeverity.P1,
    }

    def evaluate_escalation(
        self,
        incident: Incident,
        unresolved_minutes: int = 0,
        repeat_occurrence_count: int = 1,
        notification_configured: bool = False,
    ) -> EscalationResult:
        prev_sev = incident.severity
        curr_sev = prev_sev
        should_escalate = False

        # Escalation criteria: unresolved > 30 mins or > 5 occurrences
        if unresolved_minutes >= 30 or repeat_occurrence_count >= 5:
            if prev_sev != IncidentSeverity.P1:
                curr_sev = self.ESCALATION_LADDER[prev_sev]
                should_escalate = True

        if should_escalate:
            incident.severity = curr_sev

        notification_status = (
            NotificationReadiness.NOTIFICATION_SIMULATED
            if not notification_configured
            else NotificationReadiness.NOTIFICATION_READY
        )

        summary = (
            f"Incident {incident.incident_id} escalated from {prev_sev.value} to {curr_sev.value}"
            if should_escalate
            else f"Incident {incident.incident_id} retained severity {curr_sev.value}"
        )

        return EscalationResult(
            incident_id=incident.incident_id,
            previous_severity=prev_sev,
            current_severity=curr_sev,
            is_escalated=should_escalate,
            notification_status=notification_status,
            summary=summary,
            details={
                "unresolved_minutes": unresolved_minutes,
                "repeat_occurrence_count": repeat_occurrence_count,
                "notification_configured": notification_configured,
            },
        )
