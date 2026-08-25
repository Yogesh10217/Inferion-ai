"""Incident Intelligence & Lifecycle Management Subsystem (Phase 5.31)."""

from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.reliability_platform.exceptions import IncidentNotFoundException, ImmutableReliabilityRecordException
from app.platform_contracts.tenant import TenantIsolationValidator
from app.platform_contracts.lifecycle import LifecycleMachine, LifecycleTransition
from app.platform_contracts.immutability import ImmutableResource, ImmutableResourceState, ImmutableResourceValidator


class IncidentStatus(str, Enum):
    DETECTED = "DETECTED"
    TRIAGED = "TRIAGED"
    INVESTIGATING = "INVESTIGATING"
    MITIGATING = "MITIGATING"
    DELEGATED = "DELEGATED"
    RESOLVED = "RESOLVED"
    VERIFIED = "VERIFIED"
    CLOSED = "CLOSED"


class IncidentSeverity(str, Enum):
    SEV_0_CRITICAL = "SEV_0_CRITICAL"
    SEV_1_HIGH = "SEV_1_HIGH"
    SEV_2_MEDIUM = "SEV_2_MEDIUM"
    SEV_3_LOW = "SEV_3_LOW"


class TimelineEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: f"tle_{uuid.uuid4().hex[:12]}")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    status: IncidentStatus
    message: str


class IncidentTimeline(BaseModel):
    events: List[TimelineEvent] = Field(default_factory=list)


class ReliabilityIncident(BaseModel):
    incident_id: str = Field(default_factory=lambda: f"inc_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    service_id: str
    title: str
    severity: IncidentSeverity = IncidentSeverity.SEV_1_HIGH
    status: IncidentStatus = IncidentStatus.DETECTED
    timeline: IncidentTimeline = Field(default_factory=IncidentTimeline)
    immutable_record: ImmutableResource = Field(default_factory=lambda: ImmutableResource(resource_id="", tenant_id=""))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def model_post_init(self, __context: Any) -> None:
        if not self.immutable_record.resource_id:
            self.immutable_record = ImmutableResource(
                resource_id=self.incident_id,
                tenant_id=self.tenant_id,
            )


class IncidentManager:
    """Manages reliability incidents and enforces state machine transitions."""

    def __init__(self) -> None:
        self._incidents: Dict[str, ReliabilityIncident] = {}
        self.lifecycle_machine = LifecycleMachine(
            name="ReliabilityIncidentLifecycle",
            initial_state=IncidentStatus.DETECTED.value,
            valid_transitions=[
                LifecycleTransition(from_state="DETECTED", to_state="TRIAGED"),
                LifecycleTransition(from_state="TRIAGED", to_state="INVESTIGATING"),
                LifecycleTransition(from_state="INVESTIGATING", to_state="MITIGATING"),
                LifecycleTransition(from_state="MITIGATING", to_state="DELEGATED"),
                LifecycleTransition(from_state="DELEGATED", to_state="RESOLVED"),
                LifecycleTransition(from_state="RESOLVED", to_state="VERIFIED"),
                LifecycleTransition(from_state="VERIFIED", to_state="CLOSED"),
            ],
            terminal_states={"CLOSED"},
        )

    def create_incident(
        self,
        tenant_id: str,
        service_id: str,
        title: str,
        severity: IncidentSeverity = IncidentSeverity.SEV_1_HIGH,
    ) -> ReliabilityIncident:
        inc = ReliabilityIncident(
            tenant_id=tenant_id,
            service_id=service_id,
            title=title,
            severity=severity,
        )
        inc.timeline.events.append(TimelineEvent(status=IncidentStatus.DETECTED, message="Incident detected"))
        self._incidents[inc.incident_id] = inc
        return inc

    def transition_incident(
        self,
        incident_id: str,
        tenant_id: str,
        target_status: IncidentStatus,
        message: str = "Status updated",
    ) -> ReliabilityIncident:
        inc = self.get_incident(incident_id, tenant_id)

        # Check immutability
        if inc.immutable_record.state == ImmutableResourceState.FINALIZED:
            raise ImmutableReliabilityRecordException(incident_id)

        # Validate state transition
        self.lifecycle_machine.validate_transition(inc.status.value, target_status.value)

        inc.status = target_status
        inc.timeline.events.append(TimelineEvent(status=target_status, message=message))

        if target_status == IncidentStatus.CLOSED:
            ImmutableResourceValidator.finalize(inc.immutable_record, fingerprint=f"sha256_closed_{inc.incident_id}")

        return inc

    def get_incident(self, incident_id: str, tenant_id: str) -> ReliabilityIncident:
        inc = self._incidents.get(incident_id)
        if not inc:
            raise IncidentNotFoundException(incident_id)
        TenantIsolationValidator.validate_tenant_access(tenant_id, inc.tenant_id)
        return inc
