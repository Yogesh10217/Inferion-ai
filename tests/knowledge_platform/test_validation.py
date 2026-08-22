"""Unit tests for KnowledgeValidationEngine."""

import pytest
from app.knowledge_platform.knowledge import KnowledgeItem, KnowledgeVersion
from app.knowledge_platform.validation import KnowledgeValidationEngine


def test_knowledge_validation():
    ve = KnowledgeValidationEngine()
    item = KnowledgeItem(title="Valid Item", current_version=KnowledgeVersion(content="Content"))

    res = ve.validate_item(item, has_provenance=True)
    assert res.is_valid is True
    assert len(res.issues) == 0
