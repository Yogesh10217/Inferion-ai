"""
Tests for Critique Engine
"""

from app.reasoning.critique_engine import CritiqueEngine


def test_critique_engine():
    res = CritiqueEngine.critique_output("Valid response text", reasoning_chain=["Step 1", "Step 2"])
    assert res.is_valid is True
    assert res.confidence_score == 0.95
    assert res.hallucination_detected is False
