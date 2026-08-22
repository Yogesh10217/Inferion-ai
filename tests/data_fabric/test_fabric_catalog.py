"""Unit tests for DataCatalog."""

import pytest
from app.data_fabric.catalog import DataCatalog, Dataset, DataAsset


def test_data_catalog_search_and_scoping():
    catalog = DataCatalog()

    dataset = Dataset(
        source_id="ds_cat",
        tenant_id="tenant_cat",
        name="Customer Financial Dataset",
        description="Contains customer billing transactions",
        classification="FINANCIAL",
        assets=[DataAsset(name="transactions", asset_type="TABLE", field_count=5)],
    )
    catalog.register_dataset(dataset)

    # Scoped search
    res = catalog.search("financial", tenant_id="tenant_cat")
    assert len(res) == 1
    assert res[0].name == "Customer Financial Dataset"

    # Cross tenant search returns empty
    res_other = catalog.search("financial", tenant_id="tenant_other")
    assert len(res_other) == 0
