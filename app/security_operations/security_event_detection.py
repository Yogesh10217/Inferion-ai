"""
Security Event Detection Module for Phase 5.69.
Detects security events and integrates seamlessly with Phase 5.68 SRE Incident Management & Alert Engine.
"""

from __future__ import annotations

import hashlib
import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from app.deployment.secrets import SecretsSanitizer

try:
    from app.operations.alert_deduplication import AlertDeduplicationEngine
    from app.operations.alerting import Alert, AlertEngine, AlertSeverity, AlertStatus
    from app.operations.incident_management import Incident, IncidentManager, IncidentSeverity
    SRE_AVAILABLE = True
except ImportError:
    SRE_AVAILABLE = False
    AlertDeduplicationEngine = None
    AlertEngine = None
    IncidentManager = None
    Incident = None


class SecurityEventType(str, Enum):
    SECRET_EXPOSURE_ATTEMPT = "SECRET_EXPOSURE_ATTEMPT"
    UNAUTHORIZED_ACCESS_ATTEMPT = "UNAUTHORIZED_ACCESS_ATTEMPT"
    AUTHENTICATION_FAILURE_SPIKE = "AUTHENTICATION_FAILURE_SPIKE"
    SUSPICIOUS_REQUEST_PATTERN = "SUSPICIOUS_REQUEST_PATTERN"
    SECURITY_POLICY_VIOLATION = "SECURITY_POLICY_VIOLATION"
    ARTIFACT_TAMPERING = "ARTIFACT_TAMPERING"
    DEPENDENCY_SECURITY_FAILURE = "DEPENDENCY_SECURITY_FAILURE"
    CONTAINER_SECURITY_FAILURE = "CONTAINER_SECURITY_FAILURE"
    AUDIT_INTEGRITY_FAILURE = "AUDIT_INTEGRITY_FAILURE"


@dataclass
class SecurityEvent:
    event_id: str
    event_type: SecurityEventType
    severity: str
    source: str
    summary: str
    timestamp: str
    deployment_identity: str
    fingerprint: str = ""
    details: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.fingerprint:
            payload = {
                "id": self.event_id,
                "type": self.event_type.value if isinstance(self.event_type, Enum) else str(self.event_type),
                "severity": self.severity,
            }
            self.fingerprint = f"sha256:{hashlib.sha256(json.dumps(payload, sort_keys=True).encode('utf-8')).hexdigest()}"

    def to_dict(self) -> Dict[str, Any]:
        ev_type_str = self.event_type.value if isinstance(self.event_type, Enum) else str(self.event_type)
        return {
            "event_id": self.event_id,
            "event_type": ev_type_str,
            "severity": self.severity,
            "source": self.source,
            "summary": SecretsSanitizer.sanitize_string(self.summary),
            "timestamp": self.timestamp,
            "deployment_identity": self.deployment_identity,
            "fingerprint": self.fingerprint,
            "details": SecretsSanitizer.sanitize_structure(self.details),
        }


class SecurityEventDetector:
    """Detects security events and bridges them to Phase 5.68 Alert & Incident engines without duplicating architecture."""

    def __init__(
        self,
        incident_manager: Optional[Any] = None,
        alert_engine: Optional[Any] = None,
        alert_deduplicating_engine: Optional[Any] = None,
    ) -> None:
        if SRE_AVAILABLE:
            self.incident_manager = incident_manager or IncidentManager()
            self.alert_engine = alert_engine or AlertEngine()
            self.alert_deduplicating_engine = alert_deduplicating_engine or AlertDeduplicationEngine()
        else:
            self.incident_manager = incident_manager
            self.alert_engine = alert_engine
            self.alert_deduplicating_engine = alert_deduplicating_engine

        self.recorded_events: Dict[str, SecurityEvent] = {}

    def record_event(
        self,
        event_type: str,
        severity: str,
        description: str,
        source: str = "SECURITY_DETECTOR",
        deployment_identity: str = "dep-569-sec-001",
    ) -> SecurityEvent:
        now_iso = datetime.now(timezone.utc).isoformat()
        try:
            ev_enum = SecurityEventType(event_type)
        except ValueError:
            ev_enum = SecurityEventType.SECURITY_POLICY_VIOLATION

        event_id = f"SECEVT-{uuid.uuid4().hex[:8]}"
        sanitized_summary = SecretsSanitizer.sanitize_string(description)

        event = SecurityEvent(
            event_id=event_id,
            event_type=ev_enum,
            severity=severity,
            source=source,
            summary=sanitized_summary,
            timestamp=now_iso,
            deployment_identity=deployment_identity,
            details={"description": description},
        )
        self.recorded_events[event_id] = event

        if SRE_AVAILABLE and self.incident_manager and self.alert_engine:
            self.escalate_events_to_sre([event], deployment_identity)

        return event

    def get_events(self) -> Dict[str, SecurityEvent]:
        return self.recorded_events

    def detect_events(
        self,
        findings: List[Dict[str, Any]],
        deployment_identity: str = "dep-569-sec-001",
    ) -> List[SecurityEvent]:
        now_iso = datetime.now(timezone.utc).isoformat()
        events: List[SecurityEvent] = []

        for f in findings:
            ev_type_str = f.get("event_type", "SECURITY_POLICY_VIOLATION")
            try:
                ev_type = SecurityEventType(ev_type_str)
            except ValueError:
                ev_type = SecurityEventType.SECURITY_POLICY_VIOLATION

            ev = SecurityEvent(
                event_id=f"SECEVT-{uuid.uuid4().hex[:8]}",
                event_type=ev_type,
                severity=f.get("severity", "HIGH"),
                source=f.get("source", "SECURITY_DETECTOR"),
                summary=f.get("summary", f"Security event: {ev_type.value}"),
                timestamp=now_iso,
                deployment_identity=deployment_identity,
                details=f.get("details", {}),
            )
            events.append(ev)
            self.recorded_events[ev.event_id] = ev

        return events

    def escalate_events_to_sre(
        self,
        events: List[SecurityEvent],
        deployment_identity: str = "dep-569-sec-001",
    ) -> Optional[Any]:
        if not events or not SRE_AVAILABLE or not self.incident_manager:
            return None

        raw_alerts: List[Any] = []
        now_iso = datetime.now(timezone.utc).isoformat()

        for ev in events:
            sev_map = {
                "CRITICAL": AlertSeverity.EMERGENCY,
                "HIGH": AlertSeverity.CRITICAL,
                "MEDIUM": AlertSeverity.WARNING,
                "LOW": AlertSeverity.INFO,
            }
            alert_sev = sev_map.get(ev.severity, AlertSeverity.WARNING)

            raw_alerts.append(
                Alert(
                    alert_id=f"alert-{ev.event_id}",
                    source="SECURITY_EVENT_DETECTOR",
                    alert_type=ev.event_type.value if isinstance(ev.event_type, Enum) else str(ev.event_type),
                    service="enterprise-ai-platform",
                    severity=alert_sev,
                    status=AlertStatus.OPEN,
                    summary=f"SECURITY ALERT: {ev.summary}",
                    timestamp=now_iso,
                    deployment_identity=deployment_identity,
                    details=ev.to_dict(),
                )
            )

        dedup_alerts = self.alert_deduplicating_engine.deduplicate(raw_alerts) if self.alert_deduplicating_engine else raw_alerts

        has_emergency = any(getattr(a, 'severity', None) == AlertSeverity.EMERGENCY for a in dedup_alerts)
        inc_sev = IncidentSeverity.P1 if has_emergency else IncidentSeverity.P2

        inc = self.incident_manager.create_incident(
            title=f"Security Incident: {dedup_alerts[0].summary}",
            severity=inc_sev,
            deployment_identity=deployment_identity,
            summary=f"Security event escalation triggered {len(dedup_alerts)} security alerts.",
            evidence={"security_events_count": len(events), "alerts": [a.to_dict() for a in dedup_alerts]},
        )

        return inc
