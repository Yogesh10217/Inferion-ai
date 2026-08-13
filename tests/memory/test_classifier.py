"""
Tests for Memory Classification Engine
"""

from app.memory.memory_classifier import MemoryClassifier
from app.memory.memory_types import MemoryType, RetentionPolicy


def test_memory_classifier_rules():
    classifier = MemoryClassifier()

    res_profile = classifier.classify("I prefer Python FastAPI for building web APIs")
    assert res_profile.memory_type == MemoryType.PROFILE
    assert res_profile.importance_score >= 0.8
    assert res_profile.retention_policy == RetentionPolicy.PERMANENT

    res_sem = classifier.classify("Fact: PostgreSQL is our primary production datastore")
    assert res_sem.memory_type == MemoryType.SEMANTIC
    assert res_sem.importance_score >= 0.7

    res_ep = classifier.classify("Agent run completed successfully")
    assert res_ep.memory_type == MemoryType.EPISODIC

    res_conv = classifier.classify("What time is it in San Francisco?")
    assert res_conv.memory_type == MemoryType.CONVERSATION
