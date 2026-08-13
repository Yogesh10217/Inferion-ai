"""
Tests for Semantic Memory (Tier 3)
"""

import pytest
from app.memory.semantic_memory import SemanticMemory


def test_semantic_memory_store_update_search():
    sm = SemanticMemory("org_1", "ws_1")
    f1 = sm.store_fact("PostgreSQL is our primary DB", category="architecture", importance_score=0.9)
    f2 = sm.store_fact("Redis is used for caching", category="architecture", importance_score=0.8)

    assert f1.fact_id is not None
    assert f1.importance_score == 0.9

    updated = sm.update_fact(f1.fact_id, fact="PostgreSQL 16 is our primary DB")
    assert updated.fact == "PostgreSQL 16 is our primary DB"

    results = sm.search("DB", category="architecture")
    assert len(results) >= 1
    assert results[0].fact_id in (f1.fact_id, f2.fact_id)

    archived = sm.archive(f1.fact_id)
    assert archived.status == "ARCHIVED"


def test_semantic_memory_missing_raises_keyerror():
    sm = SemanticMemory()
    with pytest.raises(KeyError):
        sm.get_fact("sem_invalid")
