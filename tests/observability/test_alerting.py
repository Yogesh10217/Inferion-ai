"""Tests for AlertManager lifecycle."""

import pytest

from app.observability.alerting import AlertManager


@pytest.mark.asyncio
async def test_alert_lifecycle():
    am = AlertManager()

    alert = await am.trigger_alert(
        title="High Error Rate Detected",
        condition_type="HIGH_ERROR_RATE",
        level="CRITICAL",
        message="Agent error rate exceeded 20%",
        component="agent",
    )

    assert alert.status == "FIRING"
    assert alert.level == "CRITICAL"

    ack = am.acknowledge_alert(alert.alert_id, user_id="admin-user")
    assert ack.status == "ACKNOWLEDGED"
    assert ack.acknowledged_by == "admin-user"

    res = am.resolve_alert(alert.alert_id)
    assert res.status == "RESOLVED"
