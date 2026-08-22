"""Unit tests for SystemHealthManager and GracefulShutdownManager."""

import pytest
from app.reliability.health import SystemHealthManager
from app.reliability.graceful_shutdown import GracefulShutdownManager


@pytest.mark.asyncio
async def test_system_health_manager():
    health_mgr = SystemHealthManager()
    liveness = await health_mgr.check_liveness()
    readiness = await health_mgr.check_readiness()

    assert liveness["status"] == "HEALTHY"
    assert readiness["status"] == "HEALTHY"


@pytest.mark.asyncio
async def test_graceful_shutdown_sequence():
    shutdown_mgr = GracefulShutdownManager(drain_timeout_seconds=0.5)
    hook_called = False

    def shutdown_hook():
        nonlocal hook_called
        hook_called = True

    shutdown_mgr.register_shutdown_hook(shutdown_hook)
    res = await shutdown_mgr.initiate_shutdown()

    assert res["status"] == "SHUTDOWN_COMPLETED"
    assert hook_called is True
