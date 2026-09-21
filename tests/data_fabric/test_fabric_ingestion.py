"""Unit tests for Data Ingestion Engine."""

import pytest

from app.data_fabric.connector import ConnectorFactory, ConnectorRegistry
from app.data_fabric.connectors import register_all_initial_connectors
from app.data_fabric.data_source import DataSource, DataSourceType
from app.data_fabric.ingestion import DataIngestionEngine, IngestionMode, IngestionRequest


@pytest.mark.asyncio
async def test_ingestion_execution():
    reg = ConnectorRegistry()
    register_all_initial_connectors(reg)
    factory = ConnectorFactory(registry=reg)

    engine = DataIngestionEngine(connector_factory=factory)
    ds = DataSource(name="Ingest S3", source_type=DataSourceType.S3, connector_type="S3")

    req = IngestionRequest(source_id=ds.id, mode=IngestionMode.FULL_SYNC, limit=10)
    res = await engine.execute_ingestion(ds, req)

    assert res.status == "COMPLETED"
    assert res.total_records > 0
