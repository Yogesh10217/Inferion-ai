"""Unit tests for DecisionEngine evaluation."""

from app.orchestration.decisions import DecisionEngine, DecisionRule


def test_decision_table_evaluation():
    engine = DecisionEngine()
    rules = [
        DecisionRule(condition_key="amount", operator=">", threshold=10000, output_decision="REQUIRE_REVIEW"),
        DecisionRule(condition_key="amount", operator="<=", threshold=10000, output_decision="APPROVE"),
    ]

    tbl = engine.register_table("Credit Decision Table", rules=rules, tenant_id="t_dec")

    # Amount 5000 -> APPROVE
    res1 = engine.evaluate(tbl.table_id, {"amount": 5000})
    assert res1.decision == "APPROVE"
    assert res1.is_deterministic is True

    # Amount 15000 -> REQUIRE_REVIEW
    res2 = engine.evaluate(tbl.table_id, {"amount": 15000})
    assert res2.decision == "REQUIRE_REVIEW"
