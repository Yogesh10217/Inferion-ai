"""Unit tests for ChangeCorrelationEngine."""

from app.operations.change_intelligence import ChangeCorrelationEngine


def test_change_intelligence_correlation():
    engine = ChangeCorrelationEngine()
    chg = engine.record_change("DEPLOYMENT", "model_gpt4", "Deployed v2.1 model weights", tenant_id="t_chg")

    recent = engine.find_recent_changes("t_chg", "model_gpt4")
    assert len(recent) == 1
    assert recent[0].change_id == chg.change_id
