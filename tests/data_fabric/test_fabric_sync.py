"""Unit tests for DataSyncManager, checkpointing, and job lifecycle."""

import pytest
import asyncio
from app.data_fabric.data_source import DataSourceManager, DataSourceType
from app.data_fabric.sync import DataSyncManager, SyncStrategy, SyncStatus
from app.data_fabric.connector import ConnectorRegistry, ConnectorFactory
from app.data_fabric.connectors import register_all_initial_connectors
from app.data_fabric.ingestion import DataIngestionEngine


@pytest.mark.asyncio
async def test_sync_job_lifecycle_and_idempotency():
    reg = ConnectorRegistry()
    register_all_initial_connectors(reg)
    factory = ConnectorFactory(registry=reg)

    src_mgr = DataSourceManager()
    ds = src_mgr.create_source("Sync Source", DataSourceType.POSTGRES, "POSTGRES")

    ing_engine = DataIngestionEngine(connector_factory=factory)
    sync_mgr = DataSyncManager(source_manager=src_mgr, ingestion_engine=ing_engine)

    # 1. Create idempotent job
    job1 = sync_mgr.create_sync_job(source_id=ds.id, strategy=SyncStrategy.FULL, idempotency_key="idemp_100")
    job2 = sync_mgr.create_sync_job(source_id=ds.id, strategy=SyncStrategy.FULL, idempotency_key="idemp_100")
    assert job1.job_id == job2.job_id

    # 2. Run job
    updated_job = await sync_mgr.run_sync_job(job1.job_id)
    assert updated_job.status == SyncStatus.COMPLETED
    assert updated_job.processed_records > 0
    assert updated_job.checkpoint_cursor is not None
