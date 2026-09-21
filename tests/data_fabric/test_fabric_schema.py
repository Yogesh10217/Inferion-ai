"""Unit tests for Schema Discovery Engine."""

import pytest

from app.data_fabric.connector import ConnectorFactory, ConnectorRegistry
from app.data_fabric.connectors import register_all_initial_connectors
from app.data_fabric.data_source import DataSource, DataSourceType
from app.data_fabric.schema_discovery import SchemaDiscoveryEngine


@pytest.mark.asyncio
async def test_schema_discovery_and_classification():
    reg = ConnectorRegistry()
    register_all_initial_connectors(reg)
    factory = ConnectorFactory(registry=reg)

    engine = SchemaDiscoveryEngine(connector_factory=factory)
    ds = DataSource(name="PG Source", source_type=DataSourceType.POSTGRES, connector_type="POSTGRES")

    sch = await engine.discover_schema(ds)
    assert sch.version == 1
    assert len(sch.fields) > 0

    pii_fields = [f for f in sch.fields if f.classification == "PII"]
    assert len(pii_fields) >= 1
