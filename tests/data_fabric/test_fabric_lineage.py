"""Unit tests for DataLineageManager."""

from app.data_fabric.lineage import DataLineageManager


def test_lineage_graph_tracing():
    mgr = DataLineageManager()

    mgr.record_node("ds_pg", "DATA_SOURCE", "Postgres DB")
    mgr.record_node("ing_job_1", "INGESTION", "Ingestion Job")
    mgr.record_node("rag_index", "KNOWLEDGE_INDEX", "Vector Index")

    mgr.record_lineage("ds_pg", "ing_job_1", "INGESTED_BY")
    mgr.record_lineage("ing_job_1", "rag_index", "INDEXED_INTO")

    downstream = mgr.get_downstream_lineage("ds_pg")
    assert len(downstream) == 1
    assert downstream[0].node_id == "ing_job_1"

    upstream = mgr.get_upstream_lineage("rag_index")
    assert len(upstream) == 1
    assert upstream[0].node_id == "ing_job_1"
