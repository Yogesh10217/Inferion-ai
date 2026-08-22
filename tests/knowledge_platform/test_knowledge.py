"""Unit tests for KnowledgeManager creation and versioning."""

import pytest
from app.knowledge_platform.knowledge import KnowledgeManager, KnowledgeType, KnowledgeStatus


def test_knowledge_item_creation_and_version_update():
    mgr = KnowledgeManager()
    item = mgr.create_knowledge_item("Architecture Guideline", content="Use microservices", tenant_id="t_k1")

    assert item.title == "Architecture Guideline"
    assert item.status == KnowledgeStatus.ACTIVE
    assert len(item.history) == 1

    # Update version
    upd_item = mgr.update_version(item.item_id, new_content="Use modular monolith")
    assert upd_item.current_version.content == "Use modular monolith"
    assert len(upd_item.history) == 2
