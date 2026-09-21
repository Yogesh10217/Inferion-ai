"""Unit tests for KnowledgeTrustEngine evaluation."""

from app.knowledge_platform.knowledge import KnowledgeItem, KnowledgeVersion
from app.knowledge_platform.trust import KnowledgeTrustEngine, TrustDimension


def test_trust_engine_scoring():
    te = KnowledgeTrustEngine()
    item = KnowledgeItem(title="Trust Test Item", current_version=KnowledgeVersion(content="Test content"))

    score_obj = te.evaluate_trust(item, has_provenance=True)
    assert score_obj.overall_score > 80.0
    assert score_obj.dimension_scores[TrustDimension.PROVENANCE_COMPLETENESS] == 100.0
