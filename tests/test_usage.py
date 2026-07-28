import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock, patch
from app.limits.usage_service import UsageService
from app.limits.events import UsageEvent
from app.services.metrics_service import MetricsService

@pytest.fixture
def usage_service():
    metrics = MetricsService()
    session_factory = MagicMock()
    return UsageService(session_factory=session_factory, metrics=metrics)

@pytest.mark.asyncio
async def test_usage_event_emitted_async(usage_service):
    event = UsageEvent(
        organization_id="org_1",
        provider="openai",
        model="gpt-4",
        request_tokens=10,
        response_tokens=20,
    )
    
    with patch("asyncio.create_task") as mock_create_task:
        usage_service.emit(event)
        
        # Verify metrics updated synchronously
        summary = usage_service.metrics.get_limits_summary()
        assert summary["tokens_consumed"] == 30
        
        # Verify async task was scheduled
        mock_create_task.assert_called_once()
