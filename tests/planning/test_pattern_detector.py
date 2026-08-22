"""
Tests for Pattern Detector
"""

import pytest
from app.learning.pattern_detector import PatternDetector


def test_detect_patterns():
    episodes = [
        {"status": "completed"},
        {"status": "failed"},
        {"status": "failed"},
        {"status": "failed"},
    ]
    patterns = PatternDetector.detect_patterns(episodes)
    assert len(patterns) >= 1
    assert any(p.pattern_id == "pat_recurring_timeout" for p in patterns)
