from app.operations.alert_deduplication import AlertDeduplicationEngine
from app.operations.alerting import Alert, AlertSeverity, AlertStatus


def test_alert_deduplication_100_identical():
    engine = AlertDeduplicationEngine()
    raw_alerts = [
        Alert(
            alert_id=f"alert-{i}",
            source="SLO_ENGINE",
            alert_type="SLO_BREACH",
            service="enterprise-ai-platform",
            severity=AlertSeverity.CRITICAL,
            status=AlertStatus.OPEN,
            summary="SLO BREACH: Error Rate SLO - Breached threshold",
            timestamp=f"2026-09-13T09:{i:02d}:00Z",  # Different timestamps
            deployment_identity="dep-568-prod-001",
        )
        for i in range(100)
    ]

    deduped = engine.deduplicate(raw_alerts)
    assert len(deduped) == 1
    assert deduped[0].occurrence_count == 100
    assert deduped[0].fingerprint is not None
