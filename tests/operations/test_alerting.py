"""Unit tests for AlertManager deduplication, grouping, and storm suppression."""

import pytest
from app.operations.alerting import AlertManager, AlertSeverity, AlertStatus


def test_alert_trigger_deduplication_and_lifecycle():
    mgr = AlertManager()

    # 1. Trigger alert 1
    a1 = mgr.trigger_alert("HighErrorRate", "gateway", "High 5xx error rate detected", tenant_id="t_alt", severity=AlertSeverity.ERROR, resource_id="node_1")
    assert a1.deduplication_count == 1

    # 2. Trigger identical alert -> Deduplicated
    a2 = mgr.trigger_alert("HighErrorRate", "gateway", "High 5xx error rate detected", tenant_id="t_alt", severity=AlertSeverity.ERROR, resource_id="node_1")
    assert a2.alert_id == a1.alert_id
    assert a2.deduplication_count == 2

    # 3. Acknowledge and resolve
    mgr.acknowledge_alert(a1.alert_id)
    assert mgr.get_alert(a1.alert_id).status == AlertStatus.ACKNOWLEDGED

    mgr.resolve_alert(a1.alert_id)
    assert mgr.get_alert(a1.alert_id).status == AlertStatus.RESOLVED
