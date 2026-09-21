"""Unit tests for DatabaseHealthMonitor and TransactionManager."""

import pytest

from app.persistence.database_health import DatabaseHealthMonitor
from app.persistence.transaction import TransactionManager


@pytest.mark.asyncio
async def test_database_health_monitor():
    monitor = DatabaseHealthMonitor()
    health = await monitor.check_health()

    assert health["status"] == "HEALTHY"
    assert health["connected"] is True
    assert health["total_queries"] == 1


@pytest.mark.asyncio
async def test_transaction_manager_execution():
    tx_mgr = TransactionManager()

    async def dummy_tx_func(session):
        return "tx_done"

    res = await tx_mgr.execute_in_transaction(dummy_tx_func)
    assert res == "tx_done"
