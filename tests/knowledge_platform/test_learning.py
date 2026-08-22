"""Unit tests for KnowledgeLearningEngine feedback loop."""

import pytest
from app.knowledge_platform.knowledge import KnowledgeManager
from app.knowledge_platform.learning import KnowledgeLearningEngine, KnowledgeFeedbackType


def test_learning_feedback_confidence_adjustment():
    km = KnowledgeManager()
    item = km.create_knowledge_item("Feedback Item", content="Sample text", confidence_score=0.8, tenant_id="t_lrn")

    le = KnowledgeLearningEngine(knowledge_manager=km)
    fb = le.submit_feedback(item.item_id, feedback_type=KnowledgeFeedbackType.HELPFUL, submitted_by="user_alice")

    assert fb.feedback_type == KnowledgeFeedbackType.HELPFUL
    upd_item = km.get_item(item.item_id)
    assert upd_item.confidence_score == 0.85
