"""Unit tests for QuotaManager."""

import pytest
from app.governance.quota_manager import QuotaManager, QuotaDefinition
from app.security.exceptions import QuotaExceededError


def test_quota_consumption_and_limit_enforcement():
    qm = QuotaManager()
    qm.set_definition(QuotaDefinition(tenant_id="tenant_q", max_requests_per_day=3, max_tokens_per_day=100))

    # Consume allowed
    qm.consume_quota(tenant_id="tenant_q", requests=2, tokens=50)

    # Over consumption must raise QuotaExceededError
    with pytest.raises(QuotaExceededError):
        qm.consume_quota(tenant_id="tenant_q", requests=2, tokens=10)


def test_quota_release():
    qm = QuotaManager()
    qm.set_definition(QuotaDefinition(tenant_id="tenant_r", max_concurrent_executions=2))

    qm.consume_quota(tenant_id="tenant_r", concurrent_delta=2)
    with pytest.raises(QuotaExceededError):
        qm.consume_quota(tenant_id="tenant_r", concurrent_delta=1)

    qm.release_quota(tenant_id="tenant_r", concurrent_delta=1)
    qm.consume_quota(tenant_id="tenant_r", concurrent_delta=1)
