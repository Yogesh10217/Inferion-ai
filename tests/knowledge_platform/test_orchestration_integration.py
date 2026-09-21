"""Unit tests for OrchestrationKnowledgeAdapter context strategy selection."""

from app.knowledge_platform.context import ContextStrategy
from app.knowledge_platform.orchestration_integration import OrchestrationKnowledgeAdapter


def test_orchestration_context_strategy_selection():
    adapter = OrchestrationKnowledgeAdapter()

    # Risk > 70 -> RISK_AWARE
    strat_risk = adapter.select_context_strategy(risk_score=85.0)
    assert strat_risk == ContextStrategy.RISK_AWARE

    # Low budget -> COST_OPTIMIZED
    strat_cost = adapter.select_context_strategy(risk_score=10.0, max_budget=0.20)
    assert strat_cost == ContextStrategy.COST_OPTIMIZED
