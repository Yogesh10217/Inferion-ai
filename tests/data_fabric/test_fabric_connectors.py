"""Unit tests for Connector Registry and initial 10 production connectors."""

import pytest
import asyncio
from app.data_fabric.data_source import DataSource, DataSourceType
from app.data_fabric.connector import ConnectorRegistry, ConnectorFactory
from app.data_fabric.connectors import register_all_initial_connectors


@pytest.mark.asyncio
async def test_all_10_initial_production_connectors():
    reg = ConnectorRegistry()
    register_all_initial_connectors(reg)

    factory = ConnectorFactory(registry=reg)
    connector_types = ["POSTGRES", "MYSQL", "REST_API", "GRAPHQL", "S3", "GOOGLE_DRIVE", "SLACK", "GITHUB", "FILESYSTEM", "WEBHOOK"]

    for c_type in connector_types:
        ds = DataSource(name=f"Test {c_type}", source_type=DataSourceType.CUSTOM, connector_type=c_type)
        conn = factory.create_connector(ds)

        assert await conn.connect() is True
        assert await conn.validate() is True
        schema = await conn.discover_schema()
        assert isinstance(schema, dict)

        records = await conn.fetch(limit=5)
        assert isinstance(records, list)

        chk = await conn.checkpoint()
        assert chk.startswith("chk_")

        await conn.disconnect()
