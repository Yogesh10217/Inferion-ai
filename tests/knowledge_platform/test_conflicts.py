"""Unit tests for KnowledgeConflictManager conflict resolution."""

from app.knowledge_platform.conflicts import ConflictResolutionStrategy, ConflictType, KnowledgeConflictManager
from app.knowledge_platform.knowledge import KnowledgeManager, KnowledgeStatus


def test_conflict_detection_and_resolution():
    km = KnowledgeManager()
    item_a = km.create_knowledge_item(
        "Report 2026 - Source A", content="Revenue 10M", tenant_id="t_cnf", confidence_score=0.9
    )
    item_b = km.create_knowledge_item(
        "Report 2026 - Source B", content="Revenue 12M", tenant_id="t_cnf", confidence_score=0.7
    )

    cm = KnowledgeConflictManager(knowledge_manager=km)
    cnflct = cm.detect_conflict(
        item_a.item_id, item_b.item_id, conflict_type=ConflictType.FACT_CONTRADICTION, tenant_id="t_cnf"
    )

    # Resolve via CONFIDENCE strategy
    resolved = cm.resolve_conflict(cnflct.conflict_id, strategy=ConflictResolutionStrategy.CONFIDENCE)
    assert resolved.is_resolved is True
    assert resolved.resolved_item_id == item_a.item_id

    # Winner ACTIVE, loser SUPERSEDED (both preserved!)
    assert km.get_item(item_a.item_id).status == KnowledgeStatus.ACTIVE
    assert km.get_item(item_b.item_id).status == KnowledgeStatus.SUPERSEDED
