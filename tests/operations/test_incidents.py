"""Unit tests for IncidentManager lifecycle and timeline tracking."""

import pytest
from app.operations.incidents import IncidentManager, IncidentSeverity, IncidentStatus


def test_incident_lifecycle_and_timeline():
    mgr = IncidentManager()

    inc = mgr.create_incident("Database Latency Spike", tenant_id="t_inc", severity=IncidentSeverity.SEV2_HIGH, primary_resource_id="db_master")
    assert inc.status == IncidentStatus.DETECTED
    assert len(inc.timeline) == 1

    # Transition to INVESTIGATING
    mgr.update_status(inc.incident_id, IncidentStatus.INVESTIGATING, notes="SRE team engaged")
    assert mgr.get_incident(inc.incident_id).status == IncidentStatus.INVESTIGATING
    assert len(inc.timeline) == 2

    # Transition to RESOLVED
    mgr.update_status(inc.incident_id, IncidentStatus.RESOLVED, notes="Database index rebuilt")
    res_inc = mgr.get_incident(inc.incident_id)
    assert res_inc.status == IncidentStatus.RESOLVED
    assert res_inc.resolved_at is not None
