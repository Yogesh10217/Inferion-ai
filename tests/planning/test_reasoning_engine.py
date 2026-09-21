"""
Tests for Reasoning Engine
"""

from app.reasoning.reasoning_engine import ReasoningEngine


def test_reasoning_cot_and_tot():
    engine = ReasoningEngine()
    res_cot = engine.reason("Optimize DB queries", strategy="chain_of_thought")
    assert res_cot["is_valid"] is True
    assert len(res_cot["reasoning_steps"]) == 4

    res_tot = engine.reason("Optimize DB queries", strategy="tree_of_thoughts")
    assert res_tot["confidence_score"] > 0.5
