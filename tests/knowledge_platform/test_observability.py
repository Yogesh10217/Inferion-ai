"""Unit tests for KnowledgeMetricsCollector."""

from app.knowledge_platform.observability import KnowledgeMetricsCollector


def test_knowledge_metrics_collection():
    collector = KnowledgeMetricsCollector()
    collector.record_retrieval("t_obs", "HYBRID", 5)
    collector.record_context_tokens("t_obs", 1200)
