"""Security Incident Lifecycle Management Subsystem (Phase 5.32)."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List

from pydantic import BaseModel, Field

from app.platform_contracts.immutability import ImmutableResource, ImmutableResourceState, ImmutableResourceValidator
from app.platform_contracts.lifecycle import LifecycleMachine, LifecycleTransition
from app.security_intelligence.exceptions import (
    CrossTenantSecurityAccessException,
    ImmutableSecurityRecordException,
    InvalidSecurityIncidentTransitionException,
    SecurityIncidentNotFoundException,
)


class SecurityIncidentStatus(str, Enum):
    DETECTED = "DETECTED"
    TRIAGED = "TRIAGED"
    INVESTIGATING = "INVESTIGATING"
    CONTAINMENT_PLANNED = "CONTAINMENT_PLANNED"
    REMEDIATION_PENDING = "REMEDIATION_PENDING"
    REMEDIATION_IN_PROGRESS = "REMEDIATION_IN_PROGRESS"
    VERIFYING = "VERIFYING"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"


class SecurityIncidentSeverity(str, Enum):
    SEV_0_CRITICAL = "SEV_0_CRITICAL"
    SEV_1_HIGH = "SEV_1_HIGH"
    SEV_2_MEDIUM = "SEV_2_MEDIUM"
    SEV_3_LOW = "SEV_3_LOW"


class SecurityIncidentTimelineEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: f"site_{uuid.uuid4().hex[:12]}")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    status: SecurityIncidentStatus
    message: str


class SecurityIncident(BaseModel):
    incident_id: str = Field(default_factory=lambda: f"secinc_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    asset_id: str
    title: str
    severity: SecurityIncidentSeverity = SecurityIncidentSeverity.SEV_1_HIGH
    status: SecurityIncidentStatus = SecurityIncidentStatus.DETECTED
    timeline: List[SecurityIncidentTimelineEvent] = Field(default_factory=list)
    immutable_record: ImmutableResource = Field(default_factory=lambda: ImmutableResource(resource_id="", tenant_id=""))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def model_post_init(self, __context: Any) -> None:
        if not self.immutable_record.resource_id:
            self.immutable_record = ImmutableResource(
                resource_id=self.incident_id,
                tenant_id=self.tenant_id,
            )


class SecurityIncidentManager:
    """Manages security incidents and enforces lifecycle state transitions."""

    def __init__(self) -> None:
        self._incidents: Dict[str, SecurityIncident] = {}
        self.lifecycle_machine = LifecycleMachine(
            name="SecurityIncidentLifecycle",
            initial_state=SecurityIncidentStatus.DETECTED.value,
            valid_transitions=[
                LifecycleTransition(from_state="DETECTED", to_state="TRIAGED"),
                LifecycleTransition(from_state="TRIAGED", to_state="INVESTIGATING"),
                LifecycleTransition(from_state="INVESTIGATING", to_state="CONTAINMENT_PLANNED"),
                LifecycleTransition(from_state="CONTAINMENT_PLANNED", to_state="REMEDIATION_PENDING"),
                LifecycleTransition(from_state="REMEDIATION_PENDING", to_state="REMEDIATION_IN_PROGRESS"),
                LifecycleTransition(from_state="REMEDIATION_IN_PROGRESS", to_state="VERIFYING"),
                LifecycleTransition(from_state="VERIFYING", to_state="RESOLVED"),
                LifecycleTransition(from_state="RESOLVED", to_state="CLOSED"),
            ],
            terminal_states={"CLOSED"},
        )

    def create_incident(
        self,
        tenant_id: str,
        asset_id: str,
        title: str,
        severity: SecurityIncidentSeverity = SecurityIncidentSeverity.SEV_1_HIGH,
    ) -> SecurityIncident:
        inc = SecurityIncident(
            tenant_id=tenant_id,
            asset_id=asset_id,
            title=title,
            severity=severity,
        )
        inc.timeline.append(SecurityIncidentTimelineEvent(status=SecurityIncidentStatus.DETECTED, message="Security incident detected"))
        self._incidents[inc.incident_id] = inc
        return inc

    def transition_incident(
        self,
        incident_id: str,
        tenant_id: str,
        target_status: SecurityIncidentStatus,
        message: str = "Status updated",
    ) -> SecurityIncident:
        inc = self.get_incident(incident_id, tenant_id)

        if inc.immutable_record.state == ImmutableResourceState.FINALIZED:
            raise ImmutableSecurityRecordException(incident_id)

        try:
            self.lifecycle_machine.validate_transition(inc.status.value, target_status.value)
        except Exception as e:
            raise InvalidSecurityIncidentTransitionException(inc.status.value, target_status.value) from e

        inc.status = target_status
        inc.timeline.append(SecurityIncidentTimelineEvent(status=target_status, message=message))

        if target_status == SecurityIncidentStatus.CLOSED:
            ImmutableResourceValidator.finalize(inc.immutable_record, fingerprint=f"sha256_secinc_{inc.incident_id}")

        return inc

    def get_incident(self, incident_id: str, tenant_id: str) -> SecurityIncident:
        inc = self._incidents.get(incident_id)
        if not inc:
            raise SecurityIncidentNotFoundException(incident_id)
        if tenant_id != "global" and inc.tenant_id != "global" and tenant_id != inc.tenant_id:
            raise CrossTenantSecurityAccessException(tenant_id, inc.tenant_id)
        return inc
