"""Unit tests for Data Source Registry & Management."""

import pytest
from app.data_fabric.data_source import DataSourceManager, DataSourceType, DataSourceStatus
from app.data_fabric.exceptions import DataSourceNotFoundException


def test_data_source_creation_and_multitenancy():
    mgr = DataSourceManager()

    ds1 = mgr.create_source(
        name="Postgres DB",
        source_type=DataSourceType.POSTGRES,
        connector_type="POSTGRES",
        tenant_id="tenant_alpha",
    )
    assert ds1.status == DataSourceStatus.ACTIVE
    assert ds1.tenant_id == "tenant_alpha"

    # Multi-tenant scoping list
    alpha_sources = mgr.list_sources(tenant_id="tenant_alpha")
    assert len(alpha_sources) == 1

    beta_sources = mgr.list_sources(tenant_id="tenant_beta")
    assert len(beta_sources) == 0


def test_data_source_not_found():
    mgr = DataSourceManager()
    with pytest.raises(DataSourceNotFoundException):
        mgr.get_source("ds_nonexistent")
