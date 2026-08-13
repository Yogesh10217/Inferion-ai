"""
Tests for Memory Ranker Engine
"""

from app.memory.memory_ranker import MemoryRanker


def test_memory_ranker_composite_score():
    ranker = MemoryRanker(similarity_weight=0.4, recency_weight=0.2, importance_weight=0.2, confidence_weight=0.2)
    candidates = [
        {"id": "1", "similarity_score": 0.9, "recency_score": 0.5, "importance_score": 0.8, "confidence_score": 0.9},
        {"id": "2", "similarity_score": 0.4, "recency_score": 0.9, "importance_score": 0.4, "confidence_score": 0.5},
    ]

    ranked = ranker.rank(candidates)
    assert len(ranked) == 2
    assert ranked[0]["id"] == "1"
    assert ranked[0]["final_score"] > ranked[1]["final_score"]
