"""
Post-Incident Report Generator Module for Phase 5.68.
Generates comprehensive postmortem reports with complete secret sanitization.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.deployment.secrets import SecretsSanitizer
from app.operations.incident_management import Incident


@dataclass
class PostIncidentReport:
    report_id: str
    incident_id: str
    severity: str
    service: str
    title: str
    summary: str
    root_cause: str
    impact_summary: str
    detection_summary: str
    mitigation_summary: str
    recovery_summary: str
    timeline: List[Dict[str, Any]]
    lessons_learned: List[str]
    action_items: List[Dict[str, Any]]
    evidence: Dict[str, Any]
    generated_at: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "report_id": self.report_id,
            "incident_id": self.incident_id,
            "severity": self.severity,
            "service": self.service,
            "title": SecretsSanitizer.sanitize_string(self.title),
            "summary": SecretsSanitizer.sanitize_string(self.summary),
            "root_cause": SecretsSanitizer.sanitize_string(self.root_cause),
            "impact_summary": SecretsSanitizer.sanitize_string(self.impact_summary),
            "detection_summary": SecretsSanitizer.sanitize_string(self.detection_summary),
            "mitigation_summary": SecretsSanitizer.sanitize_string(self.mitigation_summary),
            "recovery_summary": SecretsSanitizer.sanitize_string(self.recovery_summary),
            "timeline": SecretsSanitizer.sanitize_structure(self.timeline),
            "lessons_learned": [SecretsSanitizer.sanitize_string(l) for l in self.lessons_learned],
            "action_items": SecretsSanitizer.sanitize_structure(self.action_items),
            "evidence": SecretsSanitizer.sanitize_structure(self.evidence),
            "generated_at": self.generated_at,
        }


class PostIncidentReportGenerator:
    """Generates post-incident review (PIR) reports from resolved incidents."""

    def generate_report(
        self,
        incident: Incident,
        root_cause: str = "Unspecified technical root cause",
        impact_summary: str = "Partial service degradation",
        mitigation_summary: str = "Traffic rerouted / service restarted",
        lessons_learned: Optional[List[str]] = None,
        action_items: Optional[List[Dict[str, Any]]] = None,
    ) -> PostIncidentReport:
        now_iso = datetime.now(timezone.utc).isoformat()
        rep_id = f"pir-{incident.incident_id}"

        lessons = lessons_learned or [
            "Improve automated anomaly detection thresholds",
            "Add synthetic probe for edge dependencies",
        ]
        actions = action_items or [{"task": "Update health probe timeouts", "owner": "SRE Team", "status": "OPEN"}]

        return PostIncidentReport(
            report_id=rep_id,
            incident_id=incident.incident_id,
            severity=incident.severity.value,
            service=incident.service,
            title=SecretsSanitizer.sanitize_string(incident.title),
            summary=SecretsSanitizer.sanitize_string(incident.summary),
            root_cause=SecretsSanitizer.sanitize_string(root_cause),
            impact_summary=SecretsSanitizer.sanitize_string(impact_summary),
            detection_summary=f"Incident detected at {incident.detected_at}",
            mitigation_summary=SecretsSanitizer.sanitize_string(mitigation_summary),
            recovery_summary=f"Incident state transitioned to {incident.state.value}",
            timeline=SecretsSanitizer.sanitize_structure(incident.timeline),
            lessons_learned=[SecretsSanitizer.sanitize_string(l) for l in lessons],
            action_items=SecretsSanitizer.sanitize_structure(actions),
            evidence=SecretsSanitizer.sanitize_structure(incident.evidence),
            generated_at=now_iso,
        )
