"""Unit tests for strict multi-tenant isolation across telemetry, SLOs, alerts, and incidents."""

from app.operations.alerting import AlertManager
from app.operations.incidents import IncidentManager
from app.operations.slo import SLOManager
from app.operations.telemetry import TelemetryContext, TelemetryManager, TelemetryType


def test_strict_multi_tenant_isolation():
    t_mgr = TelemetryManager()
    slo_mgr = SLOManager()
    a_mgr = AlertManager()
    inc_mgr = IncidentManager()

    # Tenant A
    t_mgr.record_event("gateway", TelemetryType.LOG, "Tenant A log", context=TelemetryContext(tenant_id="tenant_A"))
    slo_mgr.create_slo("SLO A", 99.9, tenant_id="tenant_A")
    a_mgr.trigger_alert("Rule A", "gateway", "Alert A", tenant_id="tenant_A")
    inc_mgr.create_incident("Incident A", tenant_id="tenant_A")

    # Tenant B
    t_mgr.record_event("gateway", TelemetryType.LOG, "Tenant B log", context=TelemetryContext(tenant_id="tenant_B"))
    slo_mgr.create_slo("SLO B", 99.0, tenant_id="tenant_B")
    a_mgr.trigger_alert("Rule B", "gateway", "Alert B", tenant_id="tenant_B")
    inc_mgr.create_incident("Incident B", tenant_id="tenant_B")

    # Verify strict isolation
    assert len(t_mgr.list_events(tenant_id="tenant_A")) == 1
    assert t_mgr.list_events(tenant_id="tenant_A")[0].message == "Tenant A log"
    assert len(slo_mgr.list_slos(tenant_id="tenant_A")) == 1
    assert len(a_mgr.list_alerts(tenant_id="tenant_A")) == 1
    assert len(inc_mgr.list_incidents(tenant_id="tenant_A")) == 1
    assert inc_mgr.list_incidents(tenant_id="tenant_A")[0].title == "Incident A"

    assert len(t_mgr.list_events(tenant_id="tenant_B")) == 1
    assert len(slo_mgr.list_slos(tenant_id="tenant_B")) == 1
    assert len(a_mgr.list_alerts(tenant_id="tenant_B")) == 1
    assert len(inc_mgr.list_incidents(tenant_id="tenant_B")) == 1
