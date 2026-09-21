"""Unit tests for Deterministic Decision Explainability Engine."""

from app.intelligence_platform.decisions import DecisionManager, DecisionOption
from app.intelligence_platform.explainability import ExplainabilityEngine
from app.intelligence_platform.recommendations import RecommendationManager, RecommendationType


def test_deterministic_explanation_generation():
    dec_mgr = DecisionManager()
    opt = DecisionOption(title="Option Rollback", action_type="ROLLBACK", target_resource_id="svc_1", is_selected=True)
    dec = dec_mgr.create_decision("t1", title="Test Decision", options=[opt])

    rec_mgr = RecommendationManager()
    rec = rec_mgr.create_recommendation(
        "t1", RecommendationType.ROLLBACK_DEPLOYMENT, "Title", "Action", "svc_1", "Impact"
    )

    engine = ExplainabilityEngine()
    exp = engine.generate_explanation(dec, rec)

    assert exp.recommendation_id == rec.recommendation_id
    assert "was selected because it satisfied" in exp.why_recommended
    assert len(exp.assumptions) >= 1
