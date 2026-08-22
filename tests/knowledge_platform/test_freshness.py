"""Unit tests for FreshnessEvaluator and Data Fabric CDC event processing."""

import pytest
from app.knowledge_platform.knowledge import KnowledgeManager, KnowledgeStatus
from app.knowledge_platform.freshness import FreshnessEvaluator, StalenessReason


def test_freshness_cdc_event_processing():
    km = KnowledgeManager()
    item = km.create_knowledge_item("Database Schema", content="V1 schema", tenant_id="t_fresh", source_id="src_db_1")
    evaluator = FreshnessEvaluator(knowledge_manager=km)

    stale_ids = evaluator.process_cdc_event("src_db_1", tenant_id="t_fresh", reason=StalenessReason.SOURCE_CHANGED)
    assert item.item_id in stale_ids

    upd_item = km.get_item(item.item_id)
    assert upd_item.status == KnowledgeStatus.STALE
