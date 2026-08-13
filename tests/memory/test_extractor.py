"""
Tests for Memory Extractor Engine
"""

from app.memory.memory_extractor import MemoryExtractor


def test_memory_extractor_candidates():
    extractor = MemoryExtractor()
    text = "I prefer FastAPI.\nOur stack uses PostgreSQL.\nWe decided to use Redis for caching."
    candidates = extractor.extract_from_text(text, source="user_input")

    assert len(candidates) == 3
    types = [c.candidate_type for c in candidates]
    assert "preference" in types
    assert "technology" in types
    assert "decision" in types
