from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from fastapi import FastAPI
from app.core.config import Settings
from app.core.container import ServiceContainer
from app.core.initializer import InfrastructureInitializer
from app.main import lifespan
from app.registry.model_metadata import ModelMetadata


def test_service_container_init() -> None:
    settings = Settings(APP_NAME="Test Engine", environment="test")
    container = ServiceContainer(settings=settings)

    assert container.settings.app_name == "Test Engine"
    assert container.provider_factory is not None
    assert container.registry is not None
    assert container.request_router is not None
    assert container.inference_service is not None


@pytest.mark.asyncio
async def test_initializer_runs_successfully() -> None:
    container = ServiceContainer()

    # Mock provider health checks and list_models
    mock_provider = AsyncMock()
    mock_provider.health_check.return_value = True
    mock_provider.list_models.return_value = []

    with patch.object(container.provider_factory, "get_provider", return_value=mock_provider):
        initializer = InfrastructureInitializer(container)
        await initializer.initialize()

        mock_provider.health_check.assert_awaited()
        mock_provider.list_models.assert_awaited()


@pytest.mark.asyncio
async def test_lifespan_flow() -> None:
    app = FastAPI()
    settings = Settings(app_name="Test Lifespan")
    container = ServiceContainer(settings=settings)
    app.state.container = container

    # Mock initializer
    with patch("app.core.initializer.InfrastructureInitializer.initialize", new_callable=AsyncMock) as mock_init:
        async with lifespan(app):
            pass
        mock_init.assert_awaited_once()
