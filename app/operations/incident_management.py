"""
Incident Management Module for Phase 5.68.
Manages incident entities, severity classification (P1-P4), and integrates with the incident state machine.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
import uuid

from app.deployment.secrets import SecretsSanitizer
from app.operations.incident_state_machine import IncidentState, IncidentStateMachine


class IncidentSeverity(str, Enum):
    P1 = "P1"  # Critical platform outage
    P2 = "P2"  # Major service degradation
    P3 = "P3"  # Partial degradation
    P4 = "P4"  # Minor operational issue


class IncidentStatus(str, Enum):
    NOT_DETECTED = "NOT_DETECTED"
    DETECTED = "DETECTED"
    TRIAGING = "TRIAGING"
    CONFIRMED = "CONFIRMED"
    INVESTIGATING = "INVESTIGATING"
    MITIGATING = "MITIGATING"
    RECOVERING = "RECOVERING"
    MONITORING = "MONITORING"
    RESOLVED = "RESOLVED"
    POST_INCIDENT_REVIEW_REQUIRED = "POST_INCIDENT_REVIEW_REQUIRED"
    CLOSED = "CLOSED"


@dataclass
class Incident:
    incident_id: str
    title: str
    severity: IncidentSeverity
    state: IncidentState
    service: str
    detected_at: str
    deployment_identity: str
    summary: str
    evidence: Dict[str, Any] = field(default_factory=dict)
    acknowledged_at: Optional[str] = None
    resolved_at: Optional[str] = None
    timeline: List[Dict[str, Any]] = field(default_factory=list)

    def transition_to(self, new_state: IncidentState, actor: str = "SYSTEM", note: str = "") -> IncidentState:
        old_state = self.state
        next_state = IncidentStateMachine.transition(old_state, new_state)
        self.state = next_state
        now_iso = datetime.now(timezone.utc).isoformat()
        if next_state in (IncidentState.TRIAGING, IncidentState.CONFIRMED) and not self.acknowledged_at:
            self.acknowledged_at = now_iso
        if next_state in (IncidentState.RESOLVED, IncidentState.POST_INCIDENT_REVIEW_REQUIRED, IncidentState.CLOSED) and not self.resolved_at:
            self.resolved_at = now_iso

        self.timeline.append({
            "timestamp": now_iso,
            "from_state": old_state.value,
            "to_state": next_state.value,
            "actor": actor,
            "note": SecretsSanitizer.sanitize_string(note),
        })
        return next_state

    def to_dict(self) -> Dict[str, Any]:
        return {
            "incident_id": self.incident_id,
            "title": SecretsSanitizer.sanitize_string(self.title),
            "severity": self.severity.value,
            "state": self.state.value,
            "service": self.service,
            "detected_at": self.detected_at,
            "deployment_identity": self.deployment_identity,
            "summary": SecretsSanitizer.sanitize_string(self.summary),
            "evidence": SecretsSanitizer.sanitize_structure(self.evidence),
            "acknowledged_at": self.acknowledged_at,
            "resolved_at": self.resolved_at,
            "timeline": SecretsSanitizer.sanitize_structure(self.timeline),
        }


class IncidentManager:
    """Manages active and historical incidents with secret sanitization."""

    def __init__(self) -> None:
        self.active_incidents: Dict[str, Incident] = {}
        self.closed_incidents: Dict[str, Incident] = {}

    def create_incident(
        self,
        title: str,
        severity: IncidentSeverity,
        service: str = "enterprise-ai-platform",
        deployment_identity: str = "dep-568-prod-001",
        summary: str = "",
        evidence: Optional[Dict[str, Any]] = None,
    ) -> Incident:
        now_iso = datetime.now(timezone.utc).isoformat()
        inc_id = f"inc-{uuid.uuid4().hex[:8]}"
        sanitized_summary = SecretsSanitizer.sanitize_string(summary or title)
        sanitized_evidence = SecretsSanitizer.sanitize_structure(evidence or {})

        inc = Incident(
            incident_id=inc_id,
            title=SecretsSanitizer.sanitize_string(title),
            severity=severity,
            state=IncidentState.DETECTED,
            service=service,
            detected_at=now_iso,
            deployment_identity=deployment_identity,
            summary=sanitized_summary,
            evidence=sanitized_evidence,
            timeline=[{
                "timestamp": now_iso,
                "from_state": IncidentState.NOT_DETECTED.value,
                "to_state": IncidentState.DETECTED.value,
                "actor": "SYSTEM",
                "note": "Incident detected and created",
            }],
        )
        self.active_incidents[inc_id] = inc
        return inc

    def get_incident(self, incident_id: str) -> Optional[Incident]:
        return self.active_incidents.get(incident_id) or self.closed_incidents.get(incident_id)

    def transition_incident(
        self,
        incident_id: str,
        target_state: IncidentState,
        actor: str = "OPERATOR",
        note: str = "",
    ) -> Incident:
        inc = self.get_incident(incident_id)
        if not inc:
            raise KeyError(f"Incident ID {incident_id} not found")
        inc.transition_to(target_state, actor=actor, note=note)
        if target_state == IncidentState.CLOSED and incident_id in self.active_incidents:
            self.closed_incidents[incident_id] = self.active_incidents.pop(incident_id)
        return inc
