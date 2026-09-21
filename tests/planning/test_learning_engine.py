"""
Tests for Learning Engine
"""

from app.learning.learning_engine import LearningEngine


def test_learn_from_episode():
    engine = LearningEngine()
    data = {
        "status": "completed",
        "history": [{"status": "completed"}, {"status": "completed"}],
    }
    res = engine.learn_from_episode("ep_200", data, tenant_id="tenant_x")

    assert res["status"] == "completed"
    assert len(res["patterns_detected"]) >= 1
    assert res["optimization_recommendation"] is not None
