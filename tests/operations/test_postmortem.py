"""Unit tests for PostmortemManager."""

from app.operations.incidents import Incident, IncidentSeverity
from app.operations.postmortem import PostmortemManager


def test_postmortem_generation():
    mgr = PostmortemManager()
    inc = Incident(
        title="API Gateway Outage",
        tenant_id="t_pm",
        severity=IncidentSeverity.SEV1_CRITICAL,
        primary_resource_id="gateway_api",
    )

    pm = mgr.generate_postmortem(
        incident=inc,
        root_cause_summary="Memory leak in custom middleware",
        corrective_actions=["Patch middleware memory allocation"],
        preventive_actions=["Add memory leak regression tests"],
    )

    assert pm.incident_id == inc.incident_id
    assert pm.root_cause == "Memory leak in custom middleware"
    assert len(pm.corrective_actions) == 1
