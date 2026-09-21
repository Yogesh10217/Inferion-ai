from unittest.mock import AsyncMock, MagicMock

import pytest

from app.limits.exceptions import QuotaExceededException
from app.limits.models import QuotaPolicy, QuotaWindow
from app.limits.quota_service import QuotaService
from app.services.metrics_service import MetricsService


@pytest.fixture
def mock_session():
    session = AsyncMock()
    return session


@pytest.fixture
def mock_session_factory(mock_session):
    def factory():
        return mock_session

    # Need to simulate async context manager
    mock_ctx = AsyncMock()
    mock_ctx.__aenter__.return_value = mock_session
    mock_ctx.__aexit__.return_value = None

    factory_mock = MagicMock(return_value=mock_ctx)
    return factory_mock


@pytest.fixture
def quota_service(mock_session_factory):
    metrics = MetricsService()
    return QuotaService(session_factory=mock_session_factory, metrics=metrics)


@pytest.mark.asyncio
async def test_evaluate_quotas_allowed(quota_service, mock_session):
    # Setup mock to return no policies
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = mock_result

    # Should pass without exception
    await quota_service.evaluate_quotas(organization_id="org_1")


@pytest.mark.asyncio
async def test_evaluate_quotas_exceeded(quota_service, mock_session):
    # Setup mock to return a policy with tokens_per_day
    policy = QuotaPolicy(organization_id="org_1", tokens_per_day=1000)

    # Setup mock to return a window exceeding the limit
    window = QuotaWindow(value=1500)

    mock_result = MagicMock()
    # First call is policy, second is window
    mock_result.scalar_one_or_none.side_effect = [policy, window]
    mock_session.execute.return_value = mock_result

    with pytest.raises(QuotaExceededException) as exc:
        await quota_service.evaluate_quotas(organization_id="org_1")

    assert "Daily token quota exceeded" in str(exc.value)
