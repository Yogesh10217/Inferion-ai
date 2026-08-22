"""
Tests for Reflection Engine
"""

import pytest
from app.reasoning.reflection_engine import ReflectionEngine


def test_reflection_engine_analysis():
    engine = ReflectionEngine()
    trace = [
        {"step": 1, "status": "completed"},
        {"step": 2, "status": "failed", "error": "Connection reset"},
    ]
    analysis = engine.analyze_execution("ep_100", trace, "failed")

    assert analysis["failures_count"] == 1
    assert len(analysis["lessons_generated"]) >= 1

    recs = engine.list_recommendations()
    assert len(recs) >= 1
    assert recs[0].status == "pending_approval"
