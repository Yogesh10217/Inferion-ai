"""Unit tests for ProvenanceManager chain tracking."""

import pytest
from app.knowledge_platform.provenance import ProvenanceManager


def test_provenance_chain_creation():
    pm = ProvenanceManager()
    chain = pm.create_chain("kitem_100", tenant_id="t_prov", source_system="DataFabric_Postgres", connector_type="CDC")

    assert chain.item_id == "kitem_100"
    assert chain.source_system == "DataFabric_Postgres"
    assert chain.connector_type == "CDC"

    ret_chain = pm.get_chain("kitem_100")
    assert ret_chain.chain_id == chain.chain_id
