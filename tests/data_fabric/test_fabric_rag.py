"""Unit tests for RAG Integration."""

import pytest
from app.data_fabric.data_source import DataSource, DataSourceType
from app.data_fabric.normalization import NormalizedRecord
from app.data_fabric.rag_integration import DataSourceKnowledgeAdapter


def test_rag_indexing_from_normalized_records():
    adapter = DataSourceKnowledgeAdapter()
    ds = DataSource(name="Doc Source", source_type=DataSourceType.CUSTOM, connector_type="FILESYSTEM")


    records = [
        NormalizedRecord(source_id=ds.id, source_record_id="doc_1", payload={"title": "Policy Document", "content": "Enterprise safety policy guidelines."}),
    ]

    sync_res = adapter.index_normalized_records(ds, records)
    assert sync_res.status == "SUCCESS"
    assert sync_res.records_indexed == 1
