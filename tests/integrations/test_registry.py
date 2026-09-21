"""Unit tests for IntegrationRegistry."""

from app.integrations.integration import IntegrationStatus, IntegrationType
from app.integrations.registry import IntegrationRegistry


def test_integration_registration_and_status_update():
    reg = IntegrationRegistry()
    integ = reg.register_integration("Slack Integration", category=IntegrationType.COMMUNICATION, tenant_id="t_reg")

    assert integ.name == "Slack Integration"
    assert integ.status == IntegrationStatus.ACTIVE

    upd = reg.update_status(integ.integration_id, IntegrationStatus.DEGRADED)
    assert upd.status == IntegrationStatus.DEGRADED
