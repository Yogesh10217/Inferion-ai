"""Unit tests for KnowledgeBillingTracker FinOps cost attribution."""

from app.knowledge_platform.billing import KnowledgeBillingTracker


def test_knowledge_billing_cost_attribution():
    tracker = KnowledgeBillingTracker()
    cost = tracker.record_retrieval_cost("t_fin", items_retrieved=10, tokens=5000)
    assert cost > 0.0
